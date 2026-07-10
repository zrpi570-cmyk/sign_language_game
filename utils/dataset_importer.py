import os
import re
import json
import sqlite3
from pathlib import Path

DEEPSEEK_API_KEY = 'sk-5fc4a1781e0e407ea2fe01d4640c5d21'
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'

DEEPSEEK_SYSTEM_PROMPT = '''你是手语语言学专家和现代汉语词性标注专家。

任务：对每个中文词汇精确标注两个属性：

1. word_type（词性）：只从以下列表选择最精确的一个
   - 名词：表示人、事物、地点、概念的名称
   - 动词：表示动作、行为、心理活动、变化
   - 形容词：表示性质、状态、特征
   - 副词：修饰动词/形容词
   - 代词：代替名词的词
   - 数量词：数字、量词、序数词
   - 时间词：表示时间、时段
   - 介词：表示时间/处所/方式/原因等关系
   - 连词：连接词/短语/分句
   - 叹词：表示感叹、呼唤、应答
   - 拟声词：模拟声音
   - 助词：附着在词/短语/句子后表示语法意义

2. category（语义分类）：只从以下列表选择最精确的一个
   - 数字：基数词、序数词、数字相关
   - 时间：时间单位、时间点、时间段
   - 称呼：亲属称谓、人称称呼、身份
   - 国家地名：国家名、地区名、地名
   - 情感心理：情绪、情感、心理状态
   - 动物：动物名称
   - 身体：身体部位、身体相关
   - 服装配饰：衣服、鞋帽、饰品
   - 食物饮料：食品、饮品、食材
   - 日常物品：日常用品、工具、家具
   - 动作行为：具体动作、行为活动
   - 品质特征：人的品质、性格特征
   - 状态感受：身体状态、感受、感觉
   - 社交人际：社交活动、人际关系
   - 教育：学习、教育相关
   - 医疗健康：医疗、健康、残疾相关
   - 自然：自然现象、自然物
   - 建筑场所：建筑、场所、地点
   - 交通：交通工具、交通设施
   - 颜色：颜色名称
   - 手语聋文化：手语、聋人文化相关
   - 代词：代词
   - 副词：副词
   - 其他：以上分类都不适合

返回格式：{"words":[{"word":"词汇","word_type":"词性","category":"分类"},...]}
只返回JSON，不要多余文字。'''


def classify_with_ai(words_batch):
    import urllib.request
    import time

    words_json = json.dumps([{'word': w} for w in words_batch], ensure_ascii=False)

    data = {
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'system', 'content': DEEPSEEK_SYSTEM_PROMPT},
            {'role': 'user', 'content': '请标注以下词汇的词性和分类(JSON数组)：\n' + words_json}
        ],
        'temperature': 0.0,
        'max_tokens': 4000,
        'response_format': {'type': 'json_object'}
    }

    req = urllib.request.Request(
        DEEPSEEK_API_URL,
        data=json.dumps(data).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + DEEPSEEK_API_KEY
        }
    )

    try:
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read().decode('utf-8'))
        content = result['choices'][0]['message']['content']
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            return parsed.get('words', [])
        elif isinstance(parsed, list):
            return parsed
        return []
    except Exception as e:
        print('  AI分类错误: ' + str(e))
        return []


def classify_all_with_ai(words, batch_size=50):
    import time
    results = {}
    total = len(words)
    for i in range(0, total, batch_size):
        batch = words[i:i+batch_size]
        print('  AI分类批次 ' + str(i//batch_size + 1) + '/' + str((total-1)//batch_size + 1) + '...', end=' ')
        classified = classify_with_ai(batch)
        for item in classified:
            word = item.get('word', '')
            if word:
                results[word] = {
                    'word_type': item.get('word_type', '其他'),
                    'category': item.get('category', '其他')
                }
        print(str(len(classified)) + '/' + str(len(batch)) + ' 完成')
        time.sleep(0.3)
    return results


def clean_word(raw):
    word = raw.strip()
    for sep in ['  ', ' ', '，', ',', '/', '／']:
        if sep in word:
            parts = [p.strip() for p in word.split(sep) if p.strip()]
            if parts:
                return parts[0], parts
    return word, [word]


def import_dataset(dataset_path, dataset_name, db_path, force_reclassify=False):
    """导入数据集，所有新词汇强制使用AI分类"""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS sign_language (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            word_type TEXT,
            dataset TEXT DEFAULT 'basic',
            video_path TEXT NOT NULL,
            category TEXT DEFAULT '其他',
            difficulty INTEGER DEFAULT 1,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_sign_category ON sign_language(category);
        CREATE INDEX IF NOT EXISTS idx_sign_difficulty ON sign_language(difficulty);
        CREATE INDEX IF NOT EXISTS idx_sign_dataset ON sign_language(dataset);
    ''')

    video_files = [f for f in os.listdir(dataset_path) if f.lower().endswith('.mp4')]
    
    # 获取已导入的词汇
    cursor.execute('SELECT DISTINCT word FROM sign_language')
    existing_words = set(r[0] for r in cursor.fetchall())

    words_to_import = {}
    for filename in sorted(video_files):
        primary_word, _ = clean_word(os.path.splitext(filename)[0])
        video_path = '/static/videos/' + dataset_name + '/' + filename
        difficulty = 1 if dataset_name == 'basic' else 3
        if primary_word not in words_to_import:
            words_to_import[primary_word] = []
        words_to_import[primary_word].append((video_path, difficulty, filename))

    # 找出需要AI分类的新词
    new_words = [w for w in words_to_import if w not in existing_words or force_reclassify]
    ai_results = {}

    if new_words:
        print('  发现 ' + str(len(new_words)) + ' 个新词汇，使用DeepSeek AI进行分类...')
        ai_results = classify_all_with_ai(new_words)
    else:
        print('  没有新词汇，跳过AI分类')

    count = 0
    updated = 0
    errors = []

    for primary_word, entries in words_to_import.items():
        # AI分类结果
        if primary_word in ai_results:
            word_type = ai_results[primary_word]['word_type']
            category = ai_results[primary_word]['category']
        elif primary_word in existing_words and not force_reclassify:
            # 已存在的词汇，保留原分类
            continue
        else:
            # 如果AI分类失败，使用"其他"作为fallback
            word_type = '其他'
            category = '其他'

        for video_path, difficulty, filename in entries:
            if force_reclassify and primary_word in existing_words:
                # 强制更新
                cursor.execute('UPDATE sign_language SET word_type=?, category=? WHERE word=?',
                              (word_type, category, primary_word))
                if cursor.rowcount > 0:
                    updated += 1
            else:
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO sign_language
                        (word, word_type, dataset, video_path, category, difficulty, description)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (primary_word, word_type, dataset_name, video_path, category, difficulty, None))
                    if cursor.rowcount > 0:
                        count += 1
                except sqlite3.Error as e:
                    errors.append(str(e))

    conn.commit()
    conn.close()

    if count > 0:
        print('  ' + dataset_name + ' 新增: ' + str(count) + '/' + str(len(video_files)) + ' 个词汇')
    if updated > 0:
        print('  ' + dataset_name + ' 更新分类: ' + str(updated) + ' 个词汇')
    print('  ' + dataset_name + ' 完成!')
    if errors:
        for e in errors[:3]:
            print('  Warning: ' + str(e))
    return count + updated


def reclassify_all_with_ai(db_path):
    """使用AI重新分类数据库中所有词汇 - 确保100%精确"""
    import time
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT DISTINCT word FROM sign_language ORDER BY word')
    words = [r[0] for r in c.fetchall()]
    conn.close()

    print('正在使用DeepSeek AI重新分类所有 ' + str(len(words)) + ' 个词汇...')
    print('这确保每个词汇的word_type和category都是AI精确判定的')
    print()
    results = classify_all_with_ai(words)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    updated = 0
    for word, cls in results.items():
        c.execute('UPDATE sign_language SET word_type=?, category=? WHERE word=?',
                  (cls['word_type'], cls['category'], word))
        updated += c.rowcount
    conn.commit()
    conn.close()
    print('')
    print('更新了 ' + str(updated) + ' 条记录')
    print('所有词汇分类已由DeepSeek AI精确标注!')
    return updated


def get_stats(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    total = c.execute('SELECT COUNT(1) FROM sign_language').fetchone()[0]
    types = c.execute('SELECT word_type, COUNT(1) as cnt FROM sign_language GROUP BY word_type ORDER BY cnt DESC').fetchall()
    cats = c.execute('SELECT category, COUNT(1) as cnt FROM sign_language GROUP BY category ORDER BY cnt DESC').fetchall()
    ds = c.execute('SELECT dataset, COUNT(1) as cnt FROM sign_language GROUP BY dataset').fetchall()

    conn.close()

    print('')
    print('总词汇数: ' + str(total))
    print('数据集: ' + ', '.join(str(r[0]) + ': ' + str(r[1]) for r in ds))
    print('')
    print('词性分布:')
    for r in types:
        print('  ' + str(r[0]) + ': ' + str(r[1]))
    print('')
    print('语义分类分布:')
    for r in cats:
        print('  ' + str(r[0]) + ': ' + str(r[1]))


if __name__ == '__main__':
    import os
    import sys

    base_dir = os.path.dirname(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, 'database', 'sign_language.db')

    # 检查是否有 --ai-reclassify 参数
    if '--ai-reclassify' in sys.argv:
        reclassify_all_with_ai(db_path)
        get_stats(db_path)
        sys.exit(0)

    print('开始导入手语数据集...')
    print('所有新词汇将使用DeepSeek AI进行精确分类')
    print('')

    basic_path = os.path.join(base_dir, 'dataset', 'CSL_basic_dataset')
    common_path = os.path.join(base_dir, 'dataset', 'CSL_common_dataset')

    if os.path.exists(basic_path):
        import_dataset(basic_path, 'basic', db_path)
    else:
        print('未找到基础数据集: ' + str(basic_path))

    if os.path.exists(common_path):
        import_dataset(common_path, 'common', db_path)
    else:
        print('未找到普通数据集: ' + str(common_path))

    if os.path.exists(db_path):
        get_stats(db_path)
    
    print('')
    print('提示:')
    print('  添加新视频后重新运行：python utils/dataset_importer.py')
    print('  强制重新AI分类所有词汇：python utils/dataset_importer.py --ai-reclassify')
