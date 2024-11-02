import sqlite3
from datetime import datetime

DB_PATH = 'crypto_data.db'

# Инициализация базы данных и создание таблицы
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crypto_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            crypto TEXT,
            currency TEXT,
            price REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Функция для добавления данных о криптовалюте
def insert_crypto_price(user_id, crypto, currency, price):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO crypto_prices (user_id, crypto, currency, price, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, crypto, currency, price, datetime.now()))
    conn.commit()
    conn.close()

# Получение последних 10 записей для пользователя
def get_recent_prices(user_id, limit=10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT crypto, currency, price, timestamp FROM crypto_prices
        WHERE user_id = ?
        ORDER BY timestamp DESC LIMIT ?
    ''', (user_id, limit))
    results = cursor.fetchall()
    conn.close()
    return results
