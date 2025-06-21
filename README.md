# Receipt OCR Processing System

A web application that automatically extracts information from scanned receipts using OCR/AI techniques and stores the data in a structured SQLite database.

## Features

- **PDF Upload**: Upload scanned receipts in PDF format
- **File Validation**: Validate uploaded files to ensure they are valid PDFs
- **OCR Processing**: Extract key details from receipts using OCR/AI techniques
- **Database Storage**: Store extracted information in a structured SQLite database
- **REST APIs**: Complete API endpoints for managing and retrieving receipts
- **Duplicate Handling**: Update existing records instead of creating duplicates
- **Error Handling**: Robust error handling and validation

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **OCR**: PyTesseract (Tesseract OCR engine)
- **PDF Processing**: pdf2image and Pillow
- **API Documentation**: Auto-generated with FastAPI

## Prerequisites

### System Requirements

1. **Python 3.8+**
2. **Tesseract OCR** - Required for text extraction

### Installing Tesseract OCR

#### Windows
1. Download Tesseract installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location: `C:\Program Files\Tesseract-OCR\`
3. Add to PATH environment variable

#### macOS
```bash
brew install tesseract
```

#### Ubuntu/Debian
```bash
sudo apt-get install tesseract-ocr
```

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python main.py
```

The application will start on `http://localhost:8000`

## API Documentation

Once the application is running, you can access:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## API Endpoints

### 1. Upload Receipt
**POST** `/upload`

Upload a receipt file (PDF format only).

**Request:**
- Content-Type: `multipart/form-data`
- Body: PDF file

**Response:**
```json
{
  "id": 1,
  "file_name": "receipt.pdf",
  "file_path": "uploads/20231201_143022_receipt.pdf",
  "is_valid": false,
  "invalid_reason": null,
  "is_processed": false,
  "created_at": "2023-12-01T14:30:22",
  "updated_at": "2023-12-01T14:30:22"
}
```

### 2. Validate Receipt
**POST** `/validate`

Validate whether the uploaded file is a valid PDF.

**Request:**
- Content-Type: `application/x-www-form-urlencoded`
- Body: `file_id=1`

**Response:**
```json
{
  "id": 1,
  "file_name": "receipt.pdf",
  "file_path": "uploads/20231201_143022_receipt.pdf",
  "is_valid": true,
  "invalid_reason": null,
  "is_processed": false,
  "created_at": "2023-12-01T14:30:22",
  "updated_at": "2023-12-01T14:30:25"
}
```

### 3. Process Receipt
**POST** `/process`

Extract receipt details using OCR/AI.

**Request:**
- Content-Type: `application/x-www-form-urlencoded`
- Body: `file_id=1`

**Response:**
```json
{
  "id": 1,
  "purchased_at": "2023-11-15T10:30:00",
  "merchant_name": "WALMART",
  "total_amount": 45.67,
  "file_path": "uploads/20231201_143022_receipt.pdf",
  "created_at": "2023-12-01T14:30:30",
  "updated_at": "2023-12-01T14:30:30",
  "items": "[{\"name\": \"Milk\", \"price\": 3.99}, {\"name\": \"Bread\", \"price\": 2.49}]",
  "payment_method": "CREDIT",
  "tax_amount": 2.34,
  "subtotal": 43.33,
  "receipt_number": "12345",
  "cashier": "John Doe"
}
```

### 4. List Receipts
**GET** `/receipts?skip=0&limit=100`

List all receipts stored in the database.

**Response:**
```json
{
  "receipts": [
    {
      "id": 1,
      "purchased_at": "2023-11-15T10:30:00",
      "merchant_name": "WALMART",
      "total_amount": 45.67,
      "file_path": "uploads/20231201_143022_receipt.pdf",
      "created_at": "2023-12-01T14:30:30",
      "updated_at": "2023-12-01T14:30:30",
      "items": "[{\"name\": \"Milk\", \"price\": 3.99}]",
      "payment_method": "CREDIT",
      "tax_amount": 2.34,
      "subtotal": 43.33,
      "receipt_number": "12345",
      "cashier": "John Doe"
    }
  ],
  "total": 1
}
```

### 5. Get Receipt by ID
**GET** `/receipts/{receipt_id}`

Retrieve details of a specific receipt by its ID.

**Response:**
```json
{
  "id": 1,
  "purchased_at": "2023-11-15T10:30:00",
  "merchant_name": "WALMART",
  "total_amount": 45.67,
  "file_path": "uploads/20231201_143022_receipt.pdf",
  "created_at": "2023-12-01T14:30:30",
  "updated_at": "2023-12-01T14:30:30",
  "items": "[{\"name\": \"Milk\", \"price\": 3.99}]",
  "payment_method": "CREDIT",
  "tax_amount": 2.34,
  "subtotal": 43.33,
  "receipt_number": "12345",
  "cashier": "John Doe"
}
```

### 6. List Files
**GET** `/files`

List all uploaded files.

### 7. Get File by ID
**GET** `/files/{file_id}`

Get details of a specific uploaded file.

## Database Schema

### Receipt File Table (`receipt_file`)
| Column | Description |
|--------|-------------|
| id | Unique identifier for each uploaded file |
| file_name | Name of the uploaded file |
| file_path | Storage path of the uploaded file |
| is_valid | Indicates if the file is a valid PDF |
| invalid_reason | Reason for file being invalid (if applicable) |
| is_processed | Indicates if the file has been processed |
| created_at | Creation time (when receipt was first uploaded) |
| updated_at | Last update time |

### Receipt Table (`receipt`)
| Column | Description |
|--------|-------------|
| id | Unique identifier for each extracted receipt |
| purchased_at | Date and time of purchase (extracted from receipt) |
| merchant_name | Merchant name (extracted from receipt) |
| total_amount | Total amount spent (extracted from receipt) |
| file_path | Path to the associated scanned receipt |
| created_at | Creation time (when receipt was processed) |
| updated_at | Last update time |
| items | JSON string of purchased items |
| payment_method | Payment method used |
| tax_amount | Tax amount |
| subtotal | Subtotal before tax |
| receipt_number | Receipt/transaction number |
| cashier | Cashier name |

## Usage Examples

### Using curl

1. **Upload a receipt:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@receipt.pdf"
```

2. **Validate the uploaded file:**
```bash
curl -X POST "http://localhost:8000/validate" \
  -H "accept: application/json" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "file_id=1"
```

3. **Process the receipt:**
```bash
curl -X POST "http://localhost:8000/process" \
  -H "accept: application/json" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "file_id=1"
```

4. **List all receipts:**
```bash
curl -X GET "http://localhost:8000/receipts" \
  -H "accept: application/json"
```

### Using Python requests

```python
import requests

# Upload receipt
with open('receipt.pdf', 'rb') as f:
    response = requests.post('http://localhost:8000/upload', files={'file': f})
    file_data = response.json()
    file_id = file_data['id']

# Validate file
response = requests.post('http://localhost:8000/validate', data={'file_id': file_id})

# Process receipt
response = requests.post('http://localhost:8000/process', data={'file_id': file_id})
receipt_data = response.json()

# List receipts
response = requests.get('http://localhost:8000/receipts')
receipts = response.json()
```

## OCR Processing Details

The system uses PyTesseract to extract text from PDF receipts. The processing pipeline includes:

1. **PDF to Image Conversion**: Convert PDF pages to images using pdf2image
2. **Text Extraction**: Use Tesseract OCR to extract text from images
3. **Data Parsing**: Parse extracted text to identify:
   - Merchant name
   - Purchase date
   - Total amount
   - Individual items and prices
   - Payment method
   - Receipt number
   - Cashier information

## Error Handling

The application includes comprehensive error handling for:
- Invalid file formats
- Corrupted PDF files
- OCR processing failures
- Database errors
- Missing files

## File Storage

Uploaded files are stored in the `uploads/` directory with timestamped filenames to prevent conflicts.

## Development

### Project Structure
```
├── main.py              # FastAPI application
├── database.py          # Database models and configuration
├── ocr_processor.py     # OCR processing logic
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── uploads/            # Uploaded files directory
└── receipts.db         # SQLite database
```

### Adding New Features

1. **Extend Database Schema**: Modify models in `database.py`
2. **Add API Endpoints**: Add new routes in `main.py`
3. **Enhance OCR Processing**: Improve parsing logic in `ocr_processor.py`

## Troubleshooting

### Common Issues

1. **Tesseract not found**: Ensure Tesseract is installed and in PATH
2. **PDF conversion errors**: Check if PDF is corrupted or password-protected
3. **OCR accuracy**: Improve image quality or adjust OCR settings

### Logs

Check the console output for detailed error messages and processing information.

## License

This project is developed for the Automate Accounts Developer Hiring Assessment.

## Support

For questions or issues, please refer to the project documentation or contact the development team. 