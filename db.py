import sqlite3
from datetime import datetime

conn = sqlite3.connect("wallet.db", check_same_thread=False)
cursor = conn.cursor()

# Users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    balance REAL DEFAULT 0
)
""")

# Transactions table
cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL,
    type TEXT,
    date TEXT
)
""")

conn.commit()


def create_user(user_id, name):
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, name) VALUES (?, ?)",
        (user_id, name)
    )
    conn.commit()


def get_balance(user_id):
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0


def add_balance(user_id, amount):
    cursor.execute(
        "UPDATE users SET balance = balance + ? WHERE user_id=?",
        (amount, user_id)
    )
    conn.commit()


def deduct_balance(user_id, amount):
    cursor.execute(
        "UPDATE users SET balance = balance - ? WHERE user_id=?",
        (amount, user_id)
    )
    conn.commit()


def add_transaction(user_id, amount, tx_type):
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO transactions (user_id, amount, type, date) VALUES (?, ?, ?, ?)",
        (user_id, amount, tx_type, date)
    )
    conn.commit()


def get_history(user_id, limit=10):
    cursor.execute(
        "SELECT amount, type, date FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    )
    return cursor.fetchall()


def get_all_users():
    cursor.execute("SELECT user_id, name FROM users")
    return cursor.fetchall()


def get_user_info(user_id):
    cursor.execute(
        "SELECT name, balance FROM users WHERE user_id=?",
        (user_id,)
    )
    return cursor.fetchone()
