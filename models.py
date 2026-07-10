import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "sign_language.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def hash_password(password):
    import hashlib
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL DEFAULT '',
            total_score INTEGER DEFAULT 0,
            correct_count INTEGER DEFAULT 0,
            wrong_count INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0,
            best_streak INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

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

        CREATE TABLE IF NOT EXISTS game_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            question_id INTEGER,
            is_correct BOOLEAN,
            user_answer TEXT,
            correct_answer TEXT,
            answer_time INTEGER,
            mode TEXT DEFAULT 'game',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS learning_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            sign_id INTEGER,
            mastered BOOLEAN DEFAULT 0,
            review_count INTEGER DEFAULT 0,
            correct_count INTEGER DEFAULT 0,
            wrong_count INTEGER DEFAULT 0,
            last_review DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (sign_id) REFERENCES sign_language(id)
        );

        CREATE TABLE IF NOT EXISTS stage_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            stage_id INTEGER NOT NULL,
            stage_name TEXT NOT NULL,
            completed BOOLEAN DEFAULT 0,
            stars INTEGER DEFAULT 0,
            best_score INTEGER DEFAULT 0,
            words_learned INTEGER DEFAULT 0,
            total_words INTEGER DEFAULT 0,
            completed_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS sign_landmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sign_id INTEGER NOT NULL,
            hand_type TEXT DEFAULT 'right',
            landmarks TEXT NOT NULL,
            frame_count INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sign_id) REFERENCES sign_language(id)
        );

        CREATE TABLE IF NOT EXISTS camera_game_highscores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            level_id INTEGER NOT NULL,
            score INTEGER DEFAULT 0,
            stars INTEGER DEFAULT 0,
            completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE INDEX IF NOT EXISTS idx_sign_category ON sign_language(category);
        CREATE INDEX IF NOT EXISTS idx_sign_difficulty ON sign_language(difficulty);
        CREATE INDEX IF NOT EXISTS idx_sign_dataset ON sign_language(dataset);
        CREATE INDEX IF NOT EXISTS idx_lp_user ON learning_progress(user_id);
        CREATE INDEX IF NOT EXISTS idx_lp_sign ON learning_progress(sign_id);
        CREATE INDEX IF NOT EXISTS idx_sp_user ON stage_progress(user_id);
        CREATE INDEX IF NOT EXISTS idx_sp_stage ON stage_progress(stage_id);
        CREATE INDEX IF NOT EXISTS idx_sl_sign ON sign_landmarks(sign_id);
    """)

    # 兼容旧表新增列
    for tbl, col, col_def in [
        ("users", "password_hash", "TEXT DEFAULT ''"),
        ("users", "xp", "INTEGER DEFAULT 0"),
        ("users", "level", "INTEGER DEFAULT 1"),
        ("users", "best_streak", "INTEGER DEFAULT 0"),
    ]:
        try:
            c.execute(f"ALTER TABLE {tbl} ADD COLUMN {col} {col_def}")
        except:
            pass

    conn.commit()
    conn.close()

def ensure_db_dir():
    os.makedirs(os.path.join(os.path.dirname(__file__), "database"), exist_ok=True)
