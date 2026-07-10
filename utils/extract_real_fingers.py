import os, json, sqlite3, cv2, numpy as np
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "sign_language.db")

def find_video(word):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT video_path FROM sign_language WHERE word=? LIMIT 1", (word,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    parts = row[0].split("/")
    if len(parts) < 5:
        return None
    dset = "CSL_basic_dataset" if parts[3] == "basic" else "CSL_common_dataset"
    fp = os.path.join(BASE_DIR, "dataset", dset, parts[4])
    if os.path.exists(fp):
        return fp
    # fallback to static/videos symlink
    fp2 = os.path.join(BASE_DIR, "static", "videos", parts[3], parts[4])
    return fp2 if os.path.exists(fp2) else None

def detect_fingers_from_video(video_path):
    """从视频中检测手指状态，返回平均后的[拇指,食指,中指,无名指,小指]"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total <= 0:
        cap.release()
        return None
    n = min(10, max(5, total // 3))
    indices = np.linspace(0, total - 1, n, dtype=int)
    
    all_fingers = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = hands.process(rgb)
        if res.multi_hand_landmarks:
            # 取第一只手
            lms = res.multi_hand_landmarks[0].landmark
            fingers = detect_single_hand(lms)
            all_fingers.append(fingers)
    cap.release()
    
    if not all_fingers:
        return None
    
    # 平均：对每根手指取多数决
    avg = []
    for fi in range(5):
        vals = [f[fi] for f in all_fingers]
        avg.append(1 if sum(vals) > len(vals) / 2 else 0)
    return avg

def detect_single_hand(lms):
    """从21个MediaPipe landmark检测5根手指状态"""
    fingers = [0, 0, 0, 0, 0]
    
    # 拇指：拇指尖(4)到小指掌指关节(17)的距离
    t = lms[4]
    p = lms[17]
    d = ((t.x - p.x)**2 + (t.y - p.y)**2 + ((t.z or 0) - (p.z or 0))**2) ** 0.5
    fingers[0] = 1 if d > 0.15 else 0  # 调低阈值更宽容
    
    # 其他四指
    configs = [
        (5, 6, 8),   # 食指
        (9, 10, 12), # 中指
        (13, 14, 16),# 无名指
        (17, 18, 20),# 小指
    ]
    for i, (mcp_i, pip_i, tip_i) in enumerate(configs):
        mcp = lms[mcp_i]
        pip = lms[pip_i]
        tip = lms[tip_i]
        d_tip = ((tip.x - mcp.x)**2 + (tip.y - mcp.y)**2 + ((tip.z or 0) - (mcp.z or 0))**2) ** 0.5
        d_pip = ((pip.x - mcp.x)**2 + (pip.y - mcp.y)**2 + ((pip.z or 0) - (mcp.z or 0))**2) ** 0.5
        # MCP-TIP > MCP-PIP * 1.1 = 伸直（比原来1.3更宽容）
        fingers[i + 1] = 1 if d_tip > d_pip * 1.1 else 0
    
    return fingers

# 关卡定义（保持词一致）
LEVEL_WORDS = {
    1: ["一","二","三","四","五","六","八","十"],
    2: ["好","爱","不","是","有","多","少","看","大","小"],
    3: ["帮助","朋友","名字","学习","开心","生气","害怕","喜欢","家","工作"],
    4: ["双胞胎","抱","舞蹈","欢迎"],
    5: ["好","爱","一","四","五","不","多","大","喜欢","生气"],
}

LEVEL_NAMES = {
    1: {"name": "指尖数字", "icon": "1", "desc": "用手指比划出数字手势"},
    2: {"name": "手势入门", "icon": "2", "desc": "基础手语手势"},
    3: {"name": "手势进阶", "icon": "3", "desc": "更多手语手势"},
    4: {"name": "双手挑战", "icon": "4", "desc": "双手手势"},
    5: {"name": "综合大师", "icon": "5", "desc": "随机混合手势"},
}

results = []
total_words = sum(len(ws) for ws in LEVEL_WORDS.values())
processed = 0
failed = []

for lid in range(1, 6):
    words = LEVEL_WORDS[lid]
    lv_info = LEVEL_NAMES[lid]
    signs = []
    
    for word in words:
        fp = find_video(word)
        if not fp:
            failed.append(f"{word}: 找不到视频")
            continue
        
        print(f"  [{lid}] {word}...", end=" ", flush=True)
        fingers = detect_fingers_from_video(fp)
        if fingers is None:
            failed.append(f"{word}: 未检测到手")
            print("无手")
            continue
        
        pattern = "".join(str(f) for f in fingers)
        
        # 查数据库获取分类信息
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT category, word_type FROM sign_language WHERE word=? LIMIT 1", (word,))
        row = c.fetchone()
        conn.close()
        cat = row[0] if row else ""
        wtype = row[1] if row else ""
        
        hint_map = {
            "好": "竖大拇指", "爱": "食指中指伸直", "不": "食指竖起", "是": "拇指食指张开",
            "有": "五指张开", "多": "五指张开", "少": "捏合", "看": "食指中指指眼",
            "大": "竖大拇指", "小": "捏合", "一": "食指伸直", "二": "食指中指伸直",
            "三": "拇指食指中指", "四": "四指伸直", "五": "五指全张", "六": "拇指小指",
            "七": "拇指食指中指捏", "八": "拇指食指伸直", "九": "食指钩", "十": "握拳",
            "帮助": "握拳拍掌", "朋友": "食指相勾", "名字": "食指中指并拢", "学习": "食指中指指掌",
            "开心": "五指张开", "生气": "握拳", "害怕": "手指并拢", "喜欢": "竖拇指",
            "家": "指尖相触", "工作": "握拳", "双胞胎": "双手伸指", "抱": "双手张开",
            "舞蹈": "双手拇指小指", "欢迎": "双手五指张开",
        }
        
        sign_data = {
            "word": word,
            "fingers": fingers,
            "pattern": pattern,
            "hint": hint_map.get(word, pattern),
            "category": cat,
            "word_type": wtype
        }
        signs.append(sign_data)
        processed += 1
        print(pattern)
    
    results.append({
        "id": lid,
        "name": lv_info["name"],
        "icon": lv_info["icon"],
        "desc": lv_info["desc"],
        "pass_threshold": 60,  # 5中3即可通过
        "signs": signs
    })

out = os.path.join(BASE_DIR, "static", "camera_game_data.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump({"levels": results}, f, ensure_ascii=False, indent=2)

print(f"\n完成! {processed}/{total_words} 个手势 (失败 {len(failed)})")
for f in failed[:10]:
    print(f"  - {f}")
print(f"保存: {out}")
