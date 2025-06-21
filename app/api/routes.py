from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from typing import List
from app.services.file_service import FileService
from app.services.receipt_service import ReceiptService

router = APIRouter()
file_service = FileService()
receipt_service = ReceiptService()

@router.get("/")
async def root():
    return {"message": "Receipt OCR Processing System API", "version": "1.0.0"}

@router.post("/upload")
async def upload_receipt(file: UploadFile = File(...)):
    """Upload a receipt file (PDF format only)"""
    try:
        # Validate file type
        if not file.filename or not file_service.validate_file_type(file.filename):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Save file
        file_path = file_service.save_uploaded_file(file, file.filename)
        
        # Create database record
        file_id = file_service.create_file_record(file.filename, file_path)
        
        # Return file record
        file_record = {
            "id": file_id,
            "file_name": file.filename,
            "file_path": file_path,
            "is_valid": False,
            "invalid_reason": None,
            "is_processed": False,
            "created_at": None,
            "updated_at": None
        }
        
        return file_record
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@router.post("/validate")
async def validate_receipt(file_id: int = Form(...)):
    """Validate whether the uploaded file is a valid PDF"""
    try:
        # Get file record
        file_record = file_service.get_file_record(file_id)
        
        if not file_record:
            raise HTTPException(status_code=404, detail="Receipt file not found")
        
        # Validate file exists
        is_valid = file_service.file_exists(file_record[2])  # file_path is at index 2
        invalid_reason = None if is_valid else "File not found"
        
        # Update database
        file_service.update_file_validation(file_id, is_valid, invalid_reason)
        
        # Return updated file record
        return {
            "id": file_record[0],
            "file_name": file_record[1],
            "file_path": file_record[2],
            "is_valid": is_valid,
            "invalid_reason": invalid_reason,
            "is_processed": file_record[5],
            "created_at": file_record[6],
            "updated_at": None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating file: {str(e)}")

@router.post("/process")
async def process_receipt(file_id: int = Form(...)):
    """Extract receipt details using OCR/AI"""
    try:
        # Get file record
        file_record = file_service.get_file_record(file_id)
        
        if not file_record:
            raise HTTPException(status_code=404, detail="Receipt file not found")
        
        if not file_record[3]:  # is_valid is at index 3
            raise HTTPException(status_code=400, detail="Cannot process invalid PDF file")
        
        # Create receipt record
        receipt_id = receipt_service.create_receipt(file_record[2])  # file_path
        
        # Mark file as processed
        file_service.mark_file_processed(file_id)
        
        # Get and return receipt data
        receipt_data = receipt_service.get_receipt(receipt_id)
        
        return receipt_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing receipt: {str(e)}")

@router.get("/receipts")
async def list_receipts(skip: int = 0, limit: int = 100):
    """List all processed receipts"""
    return receipt_service.get_all_receipts(skip, limit)

@router.get("/receipts/{receipt_id}")
async def get_receipt(receipt_id: int):
    """Get a specific receipt by ID"""
    receipt = receipt_service.get_receipt(receipt_id)
    
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    return receipt

@router.get("/files")
async def list_files():
    """List all uploaded files"""
    return file_service.get_all_files()

@router.get("/files/{file_id}")
async def get_file(file_id: int):
    """Get a specific file by ID"""
    file_record = file_service.get_file_record(file_id)
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "id": file_record[0],
        "file_name": file_record[1],
        "file_path": file_record[2],
        "is_valid": file_record[3],
        "invalid_reason": file_record[4],
        "is_processed": file_record[5],
        "created_at": file_record[6],
        "updated_at": file_record[7]
    } 