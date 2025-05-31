import sqlite3
from datetime import datetime

DB_NAME = 'test_rag.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_application_logs():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS application_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_query TEXT,
            response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
""")

    conn.close()

def insert_log(session_id, user_query, get_response):
    conn = get_db_connection()
    conn.execute("INSERT INTO application_logs (session_id, user_query, response) VALUES (?,?,?)",
                 (session_id, user_query, get_response))
    
    conn.commit()
    conn.close()

def get_chat_history(session_id):
    conn = get_db_connection()
    create_application_logs()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM application_logs WHERE session_id = ? ORDER BY created_at DESC', (session_id,))
    message = []
    for row in cursor.fetchall():
        message.extend([
            {'role': 'user', 'content': row['user_query']},
            {'role': 'ai', 'content': row['response']}
        ])
    conn.close()
    return message

