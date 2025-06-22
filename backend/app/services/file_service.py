import os
import shutil
from datetime import datetime
from fastapi import HTTPException
from app.models.database import get_db_connection

class FileService:
    def __init__(self):
        self.upload_dir = "uploads"
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def save_uploaded_file(self, file, filename: str) -> str:
        """Save uploaded file to disk and return file path"""
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(self.upload_dir, unique_filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            return file_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    def validate_file_type(self, filename: str) -> bool:
        """Validate if file is a PDF"""
        if not filename or not filename.lower().endswith('.pdf'):
            return False
        return True
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists on disk"""
        return os.path.exists(file_path)
    
    def create_file_record(self, filename: str, file_path: str) -> int:
        """Create a new file record in database and return file ID"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO receipt_file (file_name, file_path, is_valid, is_processed, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (filename, file_path, False, False, datetime.utcnow(), datetime.utcnow()))
            
            file_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            if file_id is None:
                raise HTTPException(status_code=500, detail="Failed to create file record")
            
            return file_id
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating file record: {str(e)}")
    
    def get_file_record(self, file_id: int):
        """Get file record by ID"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM receipt_file WHERE id = ?', (file_id,))
            file_record = cursor.fetchone()
            
            conn.close()
            return file_record
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting file record: {str(e)}")
    
    def update_file_validation(self, file_id: int, is_valid: bool, invalid_reason: str | None = None):
        """Update file validation status"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE receipt_file 
                SET is_valid = ?, invalid_reason = ?, updated_at = ?
                WHERE id = ?
            ''', (is_valid, invalid_reason, datetime.utcnow(), file_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating file validation: {str(e)}")
    
    def mark_file_processed(self, file_id: int):
        """Mark file as processed"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE receipt_file 
                SET is_processed = ?, updated_at = ?
                WHERE id = ?
            ''', (True, datetime.utcnow(), file_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error marking file as processed: {str(e)}")
    
    def get_all_files(self):
        """Get all file records"""
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
            raise HTTPException(status_code=500, detail=f"Error getting all files: {str(e)}") 