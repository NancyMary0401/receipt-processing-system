import sqlite3
import os
from datetime import datetime

# Database setup
DATABASE_PATH = "receipts.db"

def init_database():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create receipt_file table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS receipt_file (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            is_valid BOOLEAN DEFAULT FALSE,
            invalid_reason TEXT,
            is_processed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create receipt table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS receipt (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            purchased_at TIMESTAMP,
            merchant_name TEXT,
            total_amount REAL,
            file_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            items TEXT,
            payment_method TEXT,
            tax_amount REAL,
            subtotal REAL,
            receipt_number TEXT,
            cashier TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get a database connection"""
    return sqlite3.connect(DATABASE_PATH)

# Initialize database on import
init_database() 