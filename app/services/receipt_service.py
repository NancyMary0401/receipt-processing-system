import json
from datetime import datetime
from fastapi import HTTPException
from app.models.database import get_db_connection

class ReceiptService:
    def __init__(self):
        pass
    
    def create_receipt(self, file_path: str) -> int:
        """Create a new receipt record and return receipt ID"""
        try:
            # Create mock receipt data (in real implementation, this would use OCR)
            receipt_data = {
                "purchased_at": datetime.utcnow(),
                "merchant_name": "Sample Store",
                "total_amount": 25.99,
                "file_path": file_path,
                "items": json.dumps([{"name": "Sample Item", "price": 25.99}]),
                "payment_method": "CREDIT",
                "tax_amount": 2.08,
                "subtotal": 23.91,
                "receipt_number": "12345",
                "cashier": "John Doe"
            }
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
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
            conn.commit()
            conn.close()
            
            if receipt_id is None:
                raise HTTPException(status_code=500, detail="Failed to create receipt record")
            
            return receipt_id
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating receipt: {str(e)}")
    
    def get_receipt(self, receipt_id: int):
        """Get receipt by ID"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM receipt WHERE id = ?', (receipt_id,))
            row = cursor.fetchone()
            
            conn.close()
            
            if not row:
                return None
            
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
    
    def get_all_receipts(self, skip: int = 0, limit: int = 100):
        """Get all receipts with pagination"""
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