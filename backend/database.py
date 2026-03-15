import sqlite3

DB_PATH = "sales.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_schema() -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    schema_lines = []
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        cols = cursor.fetchall()
        schema_lines.append(f"Table: {table}")
        for col in cols:
            schema_lines.append(f"  {col[1]} ({col[2]})")
    conn.close()
    return "\n".join(schema_lines)