import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "sift_orders.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            phone_number TEXT,
            item_name TEXT,
            quantity INTEGER,
            size TEXT,
            total_amount REAL,
            payment_status TEXT,
            delivery_address TEXT,
            raw_dm TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_order(order_data: dict, raw_dm: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO orders (
            customer_name, phone_number, item_name, quantity, 
            size, total_amount, payment_status, delivery_address, 
            raw_dm, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        order_data.get("customer_name", "Unknown"),
        order_data.get("phone_number", "Unknown"),
        order_data.get("item_name", "Unknown"),
        order_data.get("quantity", 1),
        order_data.get("size", "N/A"),
        order_data.get("total_amount", 0.0),
        order_data.get("payment_status", "Pending"),
        order_data.get("delivery_address", "Unknown"),
        raw_dm,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def fetch_all_orders() -> pd.DataFrame:
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM orders ORDER BY id DESC", conn)
    conn.close()
    return df

def delete_order(order_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
