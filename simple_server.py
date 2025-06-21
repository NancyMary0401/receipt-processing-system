from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import shutil
from datetime import datetime
import json
import sqlite3

app = FastAPI(title="Receipt OCR Processing System", version="1.0.0")

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

# Initialize database on startup
init_database()

def get_db_connection():
    """Get a database connection"""
    return sqlite3.connect(DATABASE_PATH)

@app.get("/")
async def root():
    return {"message": "Receipt OCR Processing System API", "version": "1.0.0"}

@app.post("/upload")
async def upload_receipt(file: UploadFile = File(...)):
    """Upload a receipt file (PDF format only)"""
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Store in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO receipt_file (file_name, file_path, is_valid, is_processed, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (file.filename, file_path, False, False, datetime.utcnow(), datetime.utcnow()))
        
        file_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Return file record
        file_record = {
            "id": file_id,
            "file_name": file.filename,
            "file_path": file_path,
            "is_valid": False,
            "invalid_reason": None,
            "is_processed": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        return file_record
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@app.post("/validate")
async def validate_receipt(file_id: int = Form(...)):
    """Validate whether the uploaded file is a valid PDF"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get file record
        cursor.execute('SELECT * FROM receipt_file WHERE id = ?', (file_id,))
        file_record = cursor.fetchone()
        
        if not file_record:
            conn.close()
            raise HTTPException(status_code=404, detail="Receipt file not found")
        
        # Simple validation - check if file exists
        is_valid = os.path.exists(file_record[2])  # file_path is at index 2
        invalid_reason = None if is_valid else "File not found"
        
        # Update database
        cursor.execute('''
            UPDATE receipt_file 
            SET is_valid = ?, invalid_reason = ?, updated_at = ?
            WHERE id = ?
        ''', (is_valid, invalid_reason, datetime.utcnow(), file_id))
        
        conn.commit()
        conn.close()
        
        # Return updated file record
        return {
            "id": file_record[0],
            "file_name": file_record[1],
            "file_path": file_record[2],
            "is_valid": is_valid,
            "invalid_reason": invalid_reason,
            "is_processed": file_record[5],
            "created_at": file_record[6],
            "updated_at": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating file: {str(e)}")

@app.post("/process")
async def process_receipt(file_id: int = Form(...)):
    """Extract receipt details using OCR/AI"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get file record
        cursor.execute('SELECT * FROM receipt_file WHERE id = ?', (file_id,))
        file_record = cursor.fetchone()
        
        if not file_record:
            conn.close()
            raise HTTPException(status_code=404, detail="Receipt file not found")
        
        if not file_record[3]:  # is_valid is at index 3
            conn.close()
            raise HTTPException(status_code=400, detail="Cannot process invalid PDF file")
        
        # Create mock receipt data (in real implementation, this would use OCR)
        receipt_data = {
            "purchased_at": datetime.utcnow(),
            "merchant_name": "Sample Store",
            "total_amount": 25.99,
            "file_path": file_record[2],  # file_path
            "items": json.dumps([{"name": "Sample Item", "price": 25.99}]),
            "payment_method": "CREDIT",
            "tax_amount": 2.08,
            "subtotal": 23.91,
            "receipt_number": "12345",
            "cashier": "John Doe"
        }
        
        # Insert into receipt table
        cursor.execute('''
            INSERT INTO receipt (
                purchased_at, merchant_name, total_amount, file_path, 
                items, payment_method, tax_amount, subtotal, 
                receipt_number, cashier, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            receipt_data["purchased_at"], receipt_data["merchant_name"], 
            receipt_data["total_amount"], receipt_data["file_path"],
            receipt_data["items"], receipt_data["payment_method"],
            receipt_data["tax_amount"], receipt_data["subtotal"],
            receipt_data["receipt_number"], receipt_data["cashier"],
            datetime.utcnow(), datetime.utcnow()
        ))
        
        receipt_id = cursor.lastrowid
        
        # Mark file as processed
        cursor.execute('''
            UPDATE receipt_file 
            SET is_processed = ?, updated_at = ?
            WHERE id = ?
        ''', (True, datetime.utcnow(), file_id))
        
        conn.commit()
        conn.close()
        
        # Return receipt data
        receipt_data["id"] = receipt_id
        receipt_data["created_at"] = datetime.utcnow()
        receipt_data["updated_at"] = datetime.utcnow()
        
        return receipt_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing receipt: {str(e)}")

@app.get("/receipts")
async def list_receipts(skip: int = 0, limit: int = 100):
    """List all processed receipts"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute('SELECT COUNT(*) FROM receipt')
        total = cursor.fetchone()[0]
        
        # Get receipts with pagination
        cursor.execute('''
            SELECT * FROM receipt 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (limit, skip))
        
        receipts = []
        for row in cursor.fetchall():
            receipts.append({
                "id": row[0],
                "purchased_at": row[1],
                "merchant_name": row[2],
                "total_amount": row[3],
                "file_path": row[4],
                "created_at": row[5],
                "updated_at": row[6],
                "items": row[7],
                "payment_method": row[8],
                "tax_amount": row[9],
                "subtotal": row[10],
                "receipt_number": row[11],
                "cashier": row[12]
            })
        
        conn.close()
        
        return {
            "receipts": receipts,
            "total": total
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing receipts: {str(e)}")

@app.get("/receipts/{receipt_id}")
async def get_receipt(receipt_id: int):
    """Get a specific receipt by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM receipt WHERE id = ?', (receipt_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Receipt not found")
        
        return {
            "id": row[0],
            "purchased_at": row[1],
            "merchant_name": row[2],
            "total_amount": row[3],
            "file_path": row[4],
            "created_at": row[5],
            "updated_at": row[6],
            "items": row[7],
            "payment_method": row[8],
            "tax_amount": row[9],
            "subtotal": row[10],
            "receipt_number": row[11],
            "cashier": row[12]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting receipt: {str(e)}")

@app.get("/files")
async def list_files():
    """List all uploaded files"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM receipt_file ORDER BY created_at DESC')
        
        files = []
        for row in cursor.fetchall():
            files.append({
                "id": row[0],
                "file_name": row[1],
                "file_path": row[2],
                "is_valid": row[3],
                "invalid_reason": row[4],
                "is_processed": row[5],
                "created_at": row[6],
                "updated_at": row[7]
            })
        
        conn.close()
        return files
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@app.get("/files/{file_id}")
async def get_file(file_id: int):
    """Get a specific file by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM receipt_file WHERE id = ?', (file_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "id": row[0],
            "file_name": row[1],
            "file_path": row[2],
            "is_valid": row[3],
            "invalid_reason": row[4],
            "is_processed": row[5],
            "created_at": row[6],
            "updated_at": row[7]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting file: {str(e)}") 