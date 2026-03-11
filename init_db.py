import sqlite3
import os

DB_FILE = "attendance.db"
SCHEMA_FILE = "database_schema.sql"

def init_db():
    if os.path.exists(DB_FILE):
        print(f"Database {DB_FILE} already exists.")
        # Optional: Ask user if they want to reset? For now, we'll just print.
        return

    print("Creating new database...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # with open(SCHEMA_FILE, "r") as f:
    #     schema = f.read()
    
    # SQLite doesn't support AUTO_INCREMENT syntax exactly like MySQL (uses AUTOINCREMENT)
    # But usually `INTEGER PRIMARY KEY` is enough for auto-increment in SQLite.
    # We might need to adjust the schema slightly for SQLite compatibility if the SQL is too MySQL-specific.
    # Let's adjust it on the fly or just use a modified schema string here if needed.
    # The schema has `AUTO_INCREMENT` which is MySQL. SQLite uses `AUTOINCREMENT`.
    
    # Let's read the file but replace MySQL specific keywords for SQLite compatibility
    # 1. AUTO_INCREMENT -> AUTOINCREMENT
    # 2. INT -> INTEGER (for primary keys to auto-increment)
    # 3. ENUM -> TEXT (SQLite doesn't have ENUM)
    # 4. JSON -> TEXT (SQLite doesn't have native JSON type, stored as TEXT)
    
    # Actually, let's just write a SQLite-compatible schema here to be safe, 
    # instead of trying to parse the MySQL one loosely.
    
    sqlite_schema = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        student_id TEXT,
        section TEXT,
        role TEXT DEFAULT 'student',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        code TEXT UNIQUE NOT NULL,
        start_time DATETIME NOT NULL,
        end_time DATETIME NOT NULL,
        created_by INTEGER,
        FOREIGN KEY (created_by) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        session_id INTEGER NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'Present',
        similarity_score REAL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (session_id) REFERENCES sessions(id)
    );

    CREATE TABLE IF NOT EXISTS embeddings (
        user_id INTEGER PRIMARY KEY,
        embedding_vector TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """
    
    cursor.executescript(sqlite_schema)
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
