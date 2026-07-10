import json, os, sqlite3

BASE_DIR = r"D:\视频抖音必火\文件\Sign language"
DB_PATH = os.path.join(BASE_DIR, "database", "sign_language.db")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

LEVELS = [
    {"id":1,"name":"指尖数字","icon":"1","desc":"数字手势","pass_threshold":40,
     "words":["一","二","三","四","五","六","八","十"]},
    {"id":2,"name":"手势入门","icon":"2","desc":"基础手语","pass_threshold":40,
     "words":["好","爱","不","是","有","多","少","看","大","小"]},
    {"id":3,"name":"手势进阶","icon":"3","desc":"进阶手语","pass_threshold":40,
     "words":["帮助","朋友","名字","学习","开心","生气","害怕","喜欢","家","工作"]},
    {"id":4,"name":"双手挑战","icon":"4","desc":"双手手势","pass_threshold":40,
     "words":["双胞胎","抱","舞蹈","欢迎"]},
    {"id":5,"name":"综合大师","icon":"5","desc":"混合测试","pass_threshold":40,
     "words":["好","爱","一","五","不","多","大","喜欢","生气","四"]},
]

# 参考视频不存储任何手指数据，所有检测都在浏览器端完成
results = []
for lv in LEVELS:
    signs = []
    for word in lv["words"]:
        c.execute("SELECT id, video_path, category, word_type FROM sign_language WHERE word=? LIMIT 1", (word,))
        row = c.fetchone()
        signs.append({
            "word": word,
            "id": row[0] if row else None,
            "video_path": row[1] if row else None,
            "category": row[2] if row else "",
            "word_type": row[3] if row else "",
        })
    results.append({
        "id": lv["id"],"name": lv["name"],"icon": lv["icon"],
        "desc": lv["desc"],"pass_threshold": lv["pass_threshold"],
        "signs": signs
    })
conn.close()

out = os.path.join(BASE_DIR, "static", "camera_game_data.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump({"levels": results}, f, ensure_ascii=False, indent=2)

total = sum(len(l["signs"]) for l in results)
print(f"OK {len(results)} levels, {total} signs, no finger data - all detected in browser")
