import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "aegis.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL DEFAULT 'New Chat',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            agent TEXT DEFAULT 'aegis'
        );
        
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            agent TEXT DEFAULT 'aegis',
            timestamp TEXT NOT NULL,
            FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
        );
    """)
    
    conn.commit()
    conn.close()
    print("Database initialised.")

def create_chat(title: str = "New Chat") -> int:
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO chats (title, created_at, updated_at) VALUES (?, ?, ?)",
        (title, now, now)
    )
    chat_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return chat_id

def get_chats() -> list:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, COUNT(m.id) as message_count
        FROM chats c
        LEFT JOIN messages m ON c.id = m.chat_id
        GROUP BY c.id
        ORDER BY c.updated_at DESC
    """)
    chats = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return chats

def get_chat(chat_id: int) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chats WHERE id = ?", (chat_id,))
    chat = cursor.fetchone()
    conn.close()
    return dict(chat) if chat else None

def get_messages(chat_id: int) -> list:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM messages WHERE chat_id = ? ORDER BY timestamp ASC",
        (chat_id,)
    )
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return messages

def add_message(chat_id: int, role: str, content: str, agent: str = "aegis"):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO messages (chat_id, role, content, agent, timestamp) VALUES (?, ?, ?, ?, ?)",
        (chat_id, role, content, agent, now)
    )
    cursor.execute(
        "UPDATE chats SET updated_at = ? WHERE id = ?",
        (now, chat_id)
    )
    conn.commit()
    conn.close()

def rename_chat(chat_id: int, title: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE chats SET title = ? WHERE id = ?", (title, chat_id))
    conn.commit()
    conn.close()

def delete_chat(chat_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
    cursor.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    conn.commit()
    conn.close()

def auto_title(first_message: str) -> str:
    words = first_message.strip().split()[:6]
    title = " ".join(words)
    if len(first_message.split()) > 6:
        title += "..."
    return title.capitalize()

# Initialise on import
init_db()