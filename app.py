import os
import random
import json
import hashlib
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory, abort, session
from flask_cors import CORS
from models import get_db, init_db, ensure_db_dir, hash_password

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()
CORS(app)

ensure_db_dir()
init_db()

# ── 学习阶段定义 ──
LEARNING_STAGES = [
    {'id': 1, 'name': '你好世界', 'icon': '👋', 'categories': ['称呼'], 'desc': '学习人称称呼'},  # 30
    {'id': 2, 'name': '数数大师', 'icon': '🔢', 'categories': ['数字'], 'desc': '掌握数字表达'},  # 180
    {'id': 3, 'name': '色彩身体', 'icon': '🎨', 'categories': ['颜色', '身体'], 'desc': '颜色与身体部位'},  # 36
    {'id': 4, 'name': '时间旅行', 'icon': '⏰', 'categories': ['时间'], 'desc': '学会时间表达'},  # 137
    {'id': 5, 'name': '生活百物', 'icon': '🏠', 'categories': ['日常物品', '食物饮料', '服装配饰'], 'desc': '日常物品与饮食'},  # 51
    {'id': 6, 'name': '动物世界', 'icon': '🐾', 'categories': ['动物', '自然'], 'desc': '动物与大自然'},  # 13
    {'id': 7, 'name': '动起来', 'icon': '🏃', 'categories': ['动作行为'], 'desc': '常用动作手势'},  # 64
    {'id': 8, 'name': '心情日记', 'icon': '💖', 'categories': ['情感心理', '状态感受'], 'desc': '表达情感与感受'},  # 191
    {'id': 9, 'name': '品质特征', 'icon': '⭐', 'categories': ['品质特征'], 'desc': '描述人的品质'},  # 212
    {'id': 10, 'name': '健康生活', 'icon': '💪', 'categories': ['医疗健康', '社交人际'], 'desc': '健康与社交'},  # 16
    {'id': 11, 'name': '世界各地', 'icon': '🌍', 'categories': ['国家地名', '交通', '建筑场所'], 'desc': '国家与交通'},  # 38
    {'id': 12, 'name': '聋人文化', 'icon': '🤟', 'categories': ['手语聋文化', '教育'], 'desc': '手语文化之旅'},  # 17
]

# 为每个阶段计算词数和分类
def build_stages_with_counts(conn):
    stages = []
    for s in LEARNING_STAGES:
        s_copy = dict(s)
        placeholders = ','.join(['?'] * len(s_copy['categories']))
        c = conn.cursor()
        c.execute('SELECT COUNT(DISTINCT word) FROM sign_language WHERE category IN (' + placeholders + ')', s_copy['categories'])
        total = c.fetchone()[0]
        s_copy['total_words'] = total
        stages.append(s_copy)
    return stages

# ── 辅助函数 ──

def success_response(data, msg='ok'):
    return jsonify({'code': 0, 'message': msg, 'data': data})

def error_response(msg='error', code=1):
    return jsonify({'code': code, 'message': msg})

def get_or_create_user(username):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    if not user:
        c.execute('INSERT INTO users (username) VALUES (?)', (username,))
        conn.commit()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
    conn.close()
    return dict(user)

def add_xp(user_id, amount, conn=None):
    should_close = False
    if conn is None:
        conn = get_db()
        should_close = True
    c = conn.cursor()
    c.execute('UPDATE users SET xp = xp + ? WHERE id = ?', (amount, user_id))
    c.execute('UPDATE users SET level = (xp / 100) + 1 WHERE id = ?', (user_id,))
    c.execute('SELECT xp, level FROM users WHERE id = ?', (user_id,))
    row = c.fetchone()
    if should_close:
        conn.close()
    return dict(row) if row else None

def get_next_stage_id(user_id, conn):
    c = conn.cursor()
    # 找到第一个还没完成的阶段
    for s in LEARNING_STAGES:
        c.execute('SELECT completed FROM stage_progress WHERE user_id=? AND stage_id=?', (user_id, s['id']))
        r = c.fetchone()
        if not r or not r[0]:
            return s['id']
    return None

# ── 页面路由 ──

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/camera-game')
def camera_game():
    return render_template('camera_game.html')


@app.route('/game')
def game():
    return render_template('game.html')

@app.route('/learn')
def learning():
    return render_template('learn-dashboard.html')

@app.route('/learning')
def word_library():
    return render_template('learning.html')

@app.route('/learn/stage/<int:stage_id>')
def learn_stage(stage_id):
    return render_template('learn-stage.html', stage_id=stage_id)

@app.route('/learn/review')
def learn_review():
    return render_template('learn-review.html')

# ── 视频服务 ──

@app.route('/static/videos/<dataset>/<filename>')
def serve_video(dataset, filename):
    video_dir = os.path.join(app.static_folder, 'videos', dataset)
    if not os.path.exists(os.path.join(video_dir, filename)):
        abort(404)
    return send_from_directory(video_dir, filename)

# ════════════════════════════════════════
#  📝 用户注册 / 登录
# ════════════════════════════════════════

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or len(username) < 1:
        return error_response('请输入用户名')
    if not password or len(password) < 4:
        return error_response('密码至少4位')
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    if c.fetchone():
        conn.close()
        return error_response('用户名已存在')
    pw_hash = hash_password(password)
    c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, pw_hash))
    conn.commit()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = dict(c.fetchone())
    conn.close()
    session['user_id'] = user['id']
    session['username'] = user['username']
    return success_response(user)

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return error_response('请输入用户名和密码')
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    if not user:
        return error_response('用户不存在')
    if user['password_hash'] and user['password_hash'] != hash_password(password):
        return error_response('密码错误')
    session['user_id'] = user['id']
    session['username'] = user['username']
    return success_response(dict(user))

@app.route('/api/auth/guest', methods=['POST'])
def guest_login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    if not username:
        return error_response('请输入用户名')
    user = get_or_create_user(username)
    session['user_id'] = user['id']
    session['username'] = user['username']
    return success_response(user)

@app.route('/api/auth/me')
def auth_me():
    user_id = session.get('user_id')
    if not user_id:
        return error_response('未登录')
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    if not user:
        return error_response('用户不存在')
    return success_response(dict(user))

@app.route('/api/auth/wxlogin', methods=['POST'])
def wxlogin():
    import hashlib, re
    data = request.get_json() or {}
    code = data.get('code', '')
    user_info = data.get('userInfo', {})
    if not code: return error_response('????')
    openid = 'wx_dev_' + hashlib.md5(code.encode()).hexdigest()[:12]
    nickname = user_info.get('nickName', '') or ('??' + openid[-6:])
    nickname = re.sub(r'[<>]', '', nickname)[:20]
    if not nickname: nickname = '????'
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE username = ?', (openid,))
    user = cur.fetchone()
    if user: user = dict(user)
    else:
        cur.execute('INSERT INTO users (username) VALUES (?)', (openid,))
        conn.commit()
        cur.execute('SELECT * FROM users WHERE username = ?', (openid,))
        user = dict(cur.fetchone())
    conn.close()
    session['user_id'] = user['id']
    session['username'] = user['username']
    return success_response({
        'id': user['id'], 'username': nickname, 'nickname': nickname,
        'total_score': user['total_score'], 'xp': user['xp'],
        'level': user['level'], 'streak': user['streak'],
    })

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return success_response({})

# ════════════════════════════════════════
#  📚 学习模式 API
# ════════════════════════════════════════

@app.route('/api/learn/stages')
def get_stages():
    user_id = session.get('user_id') or request.args.get('user_id', type=int)
    if not user_id:
        return error_response('请先登录')

    conn = get_db()
    stages = build_stages_with_counts(conn)
    c = conn.cursor()

    result = []
    for s in stages:
        c.execute('SELECT * FROM stage_progress WHERE user_id=? AND stage_id=?', (user_id, s['id']))
        sp = c.fetchone()
        stage_data = {
            'stage_id': s['id'],
            'name': s['name'],
            'icon': s['icon'],
            'desc': s['desc'],
            'total_words': s['total_words'],
            'completed': sp['completed'] if sp else False,
            'stars': sp['stars'] if sp else 0,
            'best_score': sp['best_score'] if sp else 0,

        }
        if s["categories"]:
            ph = ",".join(["?"] * len(s["categories"]))
            c.execute("SELECT COUNT(DISTINCT s.word) FROM sign_language s "
                      "JOIN learning_progress lp ON s.id = lp.sign_id "
                      "WHERE lp.user_id=? AND lp.mastered=1 AND s.category IN (" + ph + ")",
                      [user_id] + s["categories"])
            stage_data["words_learned"] = c.fetchone()[0]
        else:
            stage_data["words_learned"] = 0
        result.append(stage_data)

    # 用户信息
    c.execute('SELECT xp, level, streak, best_streak, total_score FROM users WHERE id=?', (user_id,))
    user = dict(c.fetchone())

    # 总进度
    total_words = sum(s['total_words'] for s in stages)
    learned_words = sum(s['words_learned'] for s in result)
    completed_stages = sum(1 for r in result if r['completed'])

    conn.close()
    return success_response({
        'stages': result,
        'user': user,
        'total_words': total_words,
        'learned_words': learned_words,
        'completed_stages': completed_stages,
        'total_stages': len(stages),
    })

@app.route('/api/learn/stage/<int:stage_id>')
def get_stage_detail(stage_id):
    user_id = session.get('user_id') or request.args.get('user_id', type=int)
    if not user_id:
        return error_response('请先登录')

    stage = None
    for s in LEARNING_STAGES:
        if s['id'] == stage_id:
            stage = s
            break
    if not stage:
        return error_response('阶段不存在')

    conn = get_db()
    c = conn.cursor()

    # 阶段中的所有词汇
    placeholders = ','.join(['?'] * len(stage['categories']))
    c.execute('SELECT s.*, lp.mastered, lp.review_count, lp.correct_count, lp.wrong_count '
              'FROM sign_language s '
              'LEFT JOIN learning_progress lp ON s.id = lp.sign_id AND lp.user_id=? '
              'WHERE s.category IN (' + placeholders + ') '
              'GROUP BY s.word ORDER BY s.id',
              [user_id] + stage['categories'])
    words = [dict(r) for r in c.fetchall()]
    for w in words:
        if w['mastered'] is None:
            w['mastered'] = False
        if w['review_count'] is None:
            w['review_count'] = 0

    # 阶段进度
    c.execute('SELECT * FROM stage_progress WHERE user_id=? AND stage_id=?', (user_id, stage_id))
    sp = c.fetchone()

    conn.close()

    mastered = sum(1 for w in words if w.get('mastered'))
    total = len(words)

    return success_response({
        'stage': stage,
        'words': words,
        'progress': {
            'completed': sp['completed'] if sp else False,
            'stars': sp['stars'] if sp else 0,
            'best_score': sp['best_score'] if sp else 0,

            'total_words': total,
            'mastered': mastered,
        }
    })

@app.route('/api/learn/quiz', methods=['POST'])
def learn_quiz():
    """阶段内练习：从指定分类出题"""
    user_id = session.get('user_id') or request.json.get('user_id')
    stage_id = request.json.get('stage_id')
    mode = request.json.get('mode', 'practice')  # practice | test

    if not user_id or not stage_id:
        return error_response('参数不完整')

    stage = None
    for s in LEARNING_STAGES:
        if s['id'] == stage_id:
            stage = s
            break
    if not stage:
        return error_response('阶段不存在')

    conn = get_db()
    c = conn.cursor()

    placeholders = ','.join(['?'] * len(stage['categories']))
    if mode == 'test':
        # 考试模式：只出没完全掌握的
        c.execute('SELECT s.* FROM sign_language s '
                  'LEFT JOIN learning_progress lp ON s.id=lp.sign_id AND lp.user_id=? '
                  'WHERE s.category IN (' + placeholders + ') '
                  'AND (lp.mastered IS NULL OR lp.mastered=0) '
                  'GROUP BY s.word ORDER BY RANDOM() LIMIT 10',
                  [user_id] + stage['categories'])
    else:
        # 练习模式：随机出
        c.execute('SELECT s.* FROM sign_language s '
                  'WHERE s.category IN (' + placeholders + ') '
                  'GROUP BY s.word ORDER BY RANDOM() LIMIT 10',
                  stage['categories'])

    questions = []
    rows = c.fetchall()
    for row in rows:
        q = dict(row)
        # 找干扰项
        c.execute("SELECT DISTINCT word FROM sign_language WHERE word!=? AND category=? ORDER BY RANDOM() LIMIT 3",
                  (q['word'], q['category']))
        wrongs = [r[0] for r in c.fetchall()]
        # 如果干扰项不够，从同数据集补充
        if len(wrongs) < 3:
            c.execute("SELECT DISTINCT word FROM sign_language WHERE word!=? AND dataset=? ORDER BY RANDOM() LIMIT ?",
                      (q['word'], q['dataset'], 3 - len(wrongs)))
            wrongs.extend([r[0] for r in c.fetchall()])

        options = [q['word']] + wrongs[:3]
        random.shuffle(options)
        questions.append({
            'question_id': q['id'],
            'word': q['word'],
            'video_path': q['video_path'],
            'options': options,
            'correct_answer': q['word'],
        })

    conn.close()
    return success_response({
        'stage_id': stage_id,
        'stage_name': stage['name'],
        'mode': mode,
        'questions': questions,
        'total': len(questions),
    })

@app.route('/api/learn/answer', methods=['POST'])
def learn_answer():
    data = request.get_json() or {}
    user_id = session.get('user_id') or data.get('user_id')
    question_id = data.get('question_id')
    answer = data.get('answer', '').strip()
    stage_id = data.get('stage_id')
    mode = data.get('mode', 'practice')

    if not all([user_id, question_id]):
        return error_response('参数不完整')

    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT word FROM sign_language WHERE id=?', (question_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return error_response('题目不存在')

    correct_answer = row[0]
    is_correct = answer == correct_answer

    # 记录
    c.execute("INSERT INTO game_records (user_id, question_id, is_correct, user_answer, correct_answer, mode) VALUES (?,?,?,?,?,?)",
              (user_id, question_id, is_correct, answer, correct_answer, 'learn_' + mode))

    if is_correct:
        # 更新学习进度
        c.execute("SELECT id, correct_count FROM learning_progress WHERE user_id=? AND sign_id=?", (user_id, question_id))
        lp = c.fetchone()
        if lp:
            new_correct = lp['correct_count'] + 1
            mastered = 1 if new_correct >= 3 else 0
            c.execute("UPDATE learning_progress SET correct_count=?, mastered=?, review_count=review_count+1, last_review=CURRENT_TIMESTAMP WHERE id=?",
                      (new_correct, mastered, lp['id']))
        else:
            c.execute("INSERT INTO learning_progress (user_id, sign_id, mastered, correct_count, review_count, last_review) VALUES (?,?,?,1,1,CURRENT_TIMESTAMP)",
                      (user_id, question_id, 1))

        # 加XP
        xp_gain = 10 if mode == 'practice' else 30
        add_xp(user_id, xp_gain, conn)
    else:
        c.execute("SELECT id FROM learning_progress WHERE user_id=? AND sign_id=?", (user_id, question_id))
        lp = c.fetchone()
        if lp:
            c.execute("UPDATE learning_progress SET wrong_count=wrong_count+1, mastered=0, review_count=review_count+1, last_review=CURRENT_TIMESTAMP WHERE id=?",
                      (lp['id'],))
        else:
            c.execute("INSERT INTO learning_progress (user_id, sign_id, mastered, wrong_count, review_count, last_review) VALUES (?,?,0,1,1,CURRENT_TIMESTAMP)",
                      (user_id, question_id))

    # 更新用户统计
    if is_correct:
        c.execute("UPDATE users SET total_score=total_score+10, correct_count=correct_count+1, streak=streak+1 WHERE id=?", (user_id,))
        c.execute("UPDATE users SET best_streak = MAX(best_streak, streak) WHERE id=?", (user_id,))
    else:
        c.execute("UPDATE users SET wrong_count=wrong_count+1, streak=0 WHERE id=?", (user_id,))

    c.execute('SELECT xp, level, streak, total_score FROM users WHERE id=?', (user_id,))
    user_stats = dict(c.fetchone())
    conn.commit()
    conn.close()

    return success_response({
        'is_correct': is_correct,
        'correct_answer': correct_answer,
        'xp_gain': xp_gain if is_correct else 0,
        'user': user_stats,
    })

@app.route('/api/learn/stage/complete', methods=['POST'])
def complete_stage():
    user_id = session.get('user_id') or request.json.get('user_id')
    stage_id = request.json.get('stage_id')
    score = request.json.get('score', 0)
    total = request.json.get('total', 1)

    if not user_id or not stage_id:
        return error_response('参数不完整')

    stage = None
    for s in LEARNING_STAGES:
        if s['id'] == stage_id:
            stage = s
            break
    if not stage:
        return error_response('阶段不存在')

    pct = score / max(total, 1)
    stars = 1 if pct >= 0.6 else (2 if pct >= 0.8 else (3 if pct >= 0.95 else 0))
    if stars < 1:
        stars = 0

    conn = get_db()
    c = conn.cursor()

    placeholders = ','.join(['?'] * len(stage['categories']))
    c.execute('SELECT COUNT(DISTINCT word) FROM sign_language WHERE category IN (' + placeholders + ')', stage['categories'])
    total_words = c.fetchone()[0]
    c.execute('SELECT COUNT(1) FROM learning_progress lp JOIN sign_language s ON lp.sign_id=s.id '
              'WHERE lp.user_id=? AND s.category IN (' + placeholders + ') AND lp.mastered=1',
              [user_id] + stage['categories'])
    learned = c.fetchone()[0]

    c.execute('SELECT * FROM stage_progress WHERE user_id=? AND stage_id=?', (user_id, stage_id))
    existing = c.fetchone()

    if existing:
        if score > existing['best_score']:
            c.execute("UPDATE stage_progress SET best_score=?, stars=MAX(stars,?), completed=1, words_learned=?, completed_at=CURRENT_TIMESTAMP WHERE id=?",
                      (score, stars, learned, existing['id']))
    else:
        c.execute("INSERT INTO stage_progress (user_id, stage_id, stage_name, completed, stars, best_score, words_learned, total_words, completed_at) VALUES (?,?,?,1,?,?,?,?,CURRENT_TIMESTAMP)",
                  (user_id, stage_id, stage['name'], stars, score, learned, total_words))

    # 加通关XP
    xp_reward = stars * 50
    add_xp(user_id, xp_reward, conn)
    c.execute('SELECT xp, level FROM users WHERE id=?', (user_id,))
    user = dict(c.fetchone())
    conn.commit()
    conn.close()

    return success_response({
        'stars': stars,
        'score': score,
        'total': total,
        'pct': round(pct * 100),
        'xp_reward': xp_reward,
        'words_learned': learned,
        'total_words': total_words,
        'user': user,
    })

# ════════════════════════════════════════
#  🔄 复习模式 API
# ════════════════════════════════════════

@app.route('/api/learn/review/words')
def get_review_words():
    user_id = session.get('user_id') or request.args.get('user_id', type=int)
    if not user_id:
        return error_response('请先登录')

    mode = request.args.get('mode', 'all')  # all | mastered | weak | new
    stage_id = request.args.get('stage_id', type=int)

    conn = get_db()
    c = conn.cursor()

    base_sql = ('SELECT s.*, lp.mastered, lp.review_count, lp.correct_count, lp.wrong_count, '
                'COALESCE(lp.correct_count, 0) - COALESCE(lp.wrong_count, 0) as score_diff '
                'FROM sign_language s '
                'LEFT JOIN learning_progress lp ON s.id=lp.sign_id AND lp.user_id=? ')
    params = [user_id]

    if stage_id:
        stage = None
        for st in LEARNING_STAGES:
            if st['id'] == stage_id:
                stage = st
                break
        if stage:
            placeholders = ','.join(['?'] * len(stage['categories']))
            base_sql += 'WHERE s.category IN (' + placeholders + ') '
            params += stage['categories']

    base_sql += 'GROUP BY s.word '

    if mode == 'mastered':
        base_sql += 'HAVING lp.mastered=1 '
    elif mode == 'weak':
        base_sql += 'HAVING lp.mastered IS NULL OR lp.mastered=0 '
    elif mode == 'new':
        base_sql += 'HAVING lp.review_count IS NULL OR lp.review_count=0 '

    count = request.args.get('count', 30, type=int)
    base_sql += 'ORDER BY score_diff ASC, RANDOM() LIMIT ?'
    params.append(count)

    c.execute(base_sql, params)
    words = [dict(r) for r in c.fetchall()]
    for w in words:
        if w['mastered'] is None:
            w['mastered'] = False
        if w['review_count'] is None:
            w['review_count'] = 0
        if w['correct_count'] is None:
            w['correct_count'] = 0
        if w['wrong_count'] is None:
            w['wrong_count'] = 0
        w['strength'] = 'weak' if not w['mastered'] else 'strong'

    conn.close()
    return success_response({'words': words, 'total': len(words)})

@app.route('/api/learn/review/flashcards')
def get_flashcards():
    """获取复习卡片，按间隔重复"""
    user_id = session.get('user_id') or request.args.get('user_id', type=int)
    stage_id = request.args.get('stage_id', type=int)
    count = request.args.get('count', 20, type=int)

    if not user_id:
        return error_response('请先登录')

    conn = get_db()
    c = conn.cursor()

    # 优先复习：没学会的 > 需要复习的 > 新词
    base = ('SELECT s.*, lp.mastered, lp.review_count, lp.correct_count, lp.wrong_count, '
            'COALESCE(lp.correct_count, 0) - COALESCE(lp.wrong_count, 0) as score_diff '
            'FROM sign_language s '
            'LEFT JOIN learning_progress lp ON s.id=lp.sign_id AND lp.user_id=? ')
    params = [user_id]

    if stage_id:
        stage = None
        for st in LEARNING_STAGES:
            if st['id'] == stage_id:
                stage = st
                break
        if stage:
            placeholders = ','.join(['?'] * len(stage['categories']))
            base += 'WHERE s.category IN (' + placeholders + ') '
            params += stage['categories']

    base += 'GROUP BY s.word ORDER BY '
    # 智能排序：未掌握优先，然后按掌握程度从低到高
    base += 'CASE WHEN lp.mastered IS NULL OR lp.mastered=0 THEN 0 ELSE 1 END, '
    base += 'score_diff ASC, RANDOM() LIMIT ?'
    params.append(count)

    c.execute(base, params)
    words = [dict(r) for r in c.fetchall()]
    for w in words:
        if w['mastered'] is None:
            w['mastered'] = False
        if w['review_count'] is None:
            w['review_count'] = 0
        w['strength'] = 3 if w['mastered'] else (1 if (w.get('correct_count') or 0) > 0 else 0)

    conn.close()
    return success_response({'words': words, 'total': len(words)})

# ════════════════════════════════════════
#  🎮 游戏模式 API (原有)
# ════════════════════════════════════════

@app.route('/api/game/question')
def get_question():
    user_id = session.get('user_id') or request.args.get('user_id', type=int)
    difficulty = request.args.get('difficulty', 1, type=int)
    dataset = request.args.get('dataset')
    category = request.args.get('category')
    if not user_id:
        return error_response('请提供用户ID')

    conn = get_db()
    c = conn.cursor()

    conditions = ['s.difficulty <= ?']
    params = [difficulty]
    if dataset and dataset != 'all':
        conditions.append('s.dataset = ?')
        params.append(dataset)
    if category:
        conditions.append('s.category = ?')
        params.append(category)

    where = ' AND '.join(conditions)
    query = ('SELECT s.* FROM sign_language s '
             'LEFT JOIN learning_progress lp ON s.id = lp.sign_id AND lp.user_id = ? '
             'WHERE ' + where + ' AND (lp.mastered IS NULL OR lp.mastered = 0) '
             'ORDER BY RANDOM() LIMIT 1')
    c.execute(query, [user_id] + params)
    correct = c.fetchone()

    if not correct:
        query = 'SELECT s.* FROM sign_language s WHERE ' + where + ' ORDER BY RANDOM() LIMIT 1'
        c.execute(query, params)
        correct = c.fetchone()

    if not correct:
        conn.close()
        return error_response('题库为空')

    correct_row = dict(correct)

    c.execute('SELECT * FROM sign_language WHERE id!=? AND category=? AND difficulty<=? ORDER BY RANDOM() LIMIT 3',
              (correct_row['id'], correct_row['category'], difficulty))
    wrong = [dict(r) for r in c.fetchall()]

    if len(wrong) < 3:
        c.execute('SELECT * FROM sign_language WHERE id!=? AND dataset=? AND difficulty<=? ORDER BY RANDOM() LIMIT ?',
                  (correct_row['id'], correct_row['dataset'], difficulty, 3 - len(wrong)))
        extra = [dict(r) for r in c.fetchall()]
        wrong.extend(extra)

    if len(wrong) < 3:
        c.execute('SELECT * FROM sign_language WHERE id!=? AND difficulty<=? ORDER BY RANDOM() LIMIT ?',
                  (correct_row['id'], difficulty, 3 - len(wrong)))
        wrong.extend([dict(r) for r in c.fetchall()])

    conn.close()

    options = [correct_row['word']] + [w['word'] for w in wrong[:3]]
    random.shuffle(options)

    return success_response({
        'question_id': correct_row['id'],
        'word': correct_row['word'],
        'video_path': correct_row['video_path'],
        'category': correct_row['category'],
        'dataset': correct_row['dataset'],
        'word_type': correct_row['word_type'],
        'difficulty': correct_row['difficulty'],
        'options': options,
        'correct_answer': correct_row['word'],
    })

@app.route('/api/game/answer', methods=['POST'])
def submit_answer():
    data = request.get_json() or {}
    user_id = session.get('user_id') or data.get('user_id')
    question_id = data.get('question_id')
    answer = data.get('answer', '').strip()
    answer_time = data.get('answer_time', 0)
    if not all([user_id, question_id]):
        return error_response('参数不完整')

    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT word FROM sign_language WHERE id=?', (question_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return error_response('题目不存在')
    correct_answer = row[0]
    is_correct = answer == correct_answer

    c.execute("INSERT INTO game_records (user_id, question_id, is_correct, user_answer, correct_answer, answer_time, mode) VALUES (?,?,?,?,?,?,'game')",
              (user_id, question_id, is_correct, answer, correct_answer, answer_time))

    if is_correct:
        c.execute('UPDATE users SET total_score=total_score+10, correct_count=correct_count+1, streak=streak+1 WHERE id=?', (user_id,))
        c.execute('UPDATE users SET best_streak = MAX(best_streak, streak) WHERE id=?', (user_id,))
    else:
        c.execute('UPDATE users SET wrong_count=wrong_count+1, streak=0 WHERE id=?', (user_id,))

    c.execute('SELECT * FROM users WHERE id=?', (user_id,))
    user = dict(c.fetchone())
    conn.commit()
    conn.close()

    return success_response({
        'is_correct': is_correct,
        'correct_answer': correct_answer,
        'user': user,
    })

# ── API: 排行榜 ──

@app.route('/api/game/ranking')
def ranking():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, username, total_score, correct_count, wrong_count, streak, best_streak, xp, level FROM users ORDER BY total_score DESC LIMIT 100')
    users = [dict(r) for r in c.fetchall()]
    c.execute('SELECT COUNT(1) FROM users')
    total_users = c.fetchone()[0]
    conn.close()
    return success_response({'users': users, 'total_users': total_users})

# ── API: 手语词汇列表 ──

@app.route('/api/learning/list')
def learning_list():
    category = request.args.get('category')
    dataset = request.args.get('dataset')
    difficulty = request.args.get('difficulty', type=int)
    word_type = request.args.get('word_type')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    conn = get_db()
    c = conn.cursor()
    conditions = []
    params = []
    if category:
        conditions.append('category = ?')
        params.append(category)
    if dataset:
        conditions.append('dataset = ?')
        params.append(dataset)
    if difficulty:
        conditions.append('difficulty = ?')
        params.append(difficulty)
    if word_type:
        conditions.append('word_type = ?')
        params.append(word_type)
    where = (' WHERE ' + ' AND '.join(conditions)) if conditions else ''

    c.execute('SELECT COUNT(1) FROM sign_language' + where, params)
    total = c.fetchone()[0]
    offset = (page - 1) * per_page
    c.execute('SELECT * FROM sign_language' + where + ' ORDER BY id LIMIT ? OFFSET ?', params + [per_page, offset])
    items = [dict(r) for r in c.fetchall()]
    conn.close()
    return success_response({'total': total, 'page': page, 'per_page': per_page, 'items': items})

# ── API: 统计 ──

@app.route('/api/sign/random-videos')
def random_videos():
    count = request.args.get('count', 8, type=int)
    conn = get_db()
    cu = conn.cursor()
    sql = 'SELECT id, word, word_type, category, video_path FROM sign_language ORDER BY ' + 'RANDOM() LIMIT ?'
    cu.execute(sql, (count,))
    videos = [dict(r) for r in cu.fetchall()]
    conn.close()
    return success_response(videos)

@app.route('/api/sign/stats')
def sign_stats():
    conn = get_db()
    c = conn.cursor()
    total = c.execute('SELECT COUNT(1) FROM sign_language').fetchone()[0]
    categories = c.execute('SELECT category, COUNT(1) as cnt FROM sign_language GROUP BY category ORDER BY cnt DESC').fetchall()
    types = c.execute('SELECT word_type, COUNT(1) as cnt FROM sign_language GROUP BY word_type ORDER BY cnt DESC').fetchall()
    datasets = c.execute('SELECT dataset, COUNT(1) as cnt FROM sign_language GROUP BY dataset').fetchall()
    conn.close()
    return success_response({
        'total': total,
        'categories': [dict(r) for r in categories],
        'types': [dict(r) for r in types],
        'datasets': [dict(r) for r in datasets],
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
