# Receipt OCR Processing System (Backend)

A backend service to extract and manage receipt data from scanned PDFs using OCR and AI.

## Features

- Upload and validate PDF receipts
- Extract receipt data using OCR (Tesseract)
- Store and manage receipts in SQLite
- RESTful API for all operations

## Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** SQLite (SQLAlchemy)
- **OCR:** PyTesseract, pdf2image, Pillow

## Prerequisites

- Python 3.8+
- Tesseract OCR (must be installed and in PATH)
- **Note:** Sometimes the `Pillow` library (used for image processing) may not install automatically with other dependencies. If you encounter errors related to `Pillow`, install it manually using:
  ```sh
  pip install Pillow
  ```

### Tesseract Installation

**Windows:**  
Download from [here](https://github.com/UB-Mannheim/tesseract/wiki) and add to PATH.

**macOS:**  
```sh
brew install tesseract
```

**Ubuntu:**  
```sh
sudo apt-get install tesseract-ocr
```

## Setup

1. **Clone the repository**
2. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```
3. **Activate the virtual environment (Windows):**
   ```sh
   venv\Scripts\activate
   ```
   *(On macOS/Linux: `source venv/bin/activate`)*
4. **Run the backend**
   ```sh
   python main.py
   ```
   The API will be available at `http://localhost:8000`

## API Endpoints

### Upload Receipt
- **POST** `/upload`
- **Body:** `form-data`, key: `file` (PDF)
- **Response:** File info (ID, name, path)

### Validate Receipt
- **POST** `/validate`
- **Body:** `x-www-form-urlencoded`, key: `file_id`
- **Response:** Validation result

### Process Receipt
- **POST** `/process`
- **Body:** `x-www-form-urlencoded`, key: `file_id`
- **Response:** Extracted receipt data

### List Receipts
- **GET** `/receipts`

### Get Receipt by ID
- **GET** `/receipts/{receipt_id}`

### List Files
- **GET** `/files`

## API Docs

- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Testing

To verify the API and its endpoints, you can run the provided test script:

1. **Ensure the virtual environment is activated** (see Setup step 3).
2. **Run the test script:**
   ```sh
   python test_api.py
   ```
   This script will test all major API endpoints and print the results in the console.

Alternatively, you can use a **Postman collection** to test the API endpoints interactively. Simply import the API requests into Postman and configure the base URL as needed.

# Running the Backend Server

To start the FastAPI backend server in development mode (with auto-reload), run the following command from inside the `receipt-processing-system` directory:

```
uvicorn app.main:app --reload
```

This will start the server at http://localhost:8000.

You can access the interactive API docs at http://localhost:8000/docs.