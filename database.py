import sqlite3


def init_db():
    conn = sqlite3.connect("stress.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS stress_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            cam_rate REAL,
            mic_rate REAL,
            voice_score REAL,
            final_score REAL,
            level TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database created successfully.")
