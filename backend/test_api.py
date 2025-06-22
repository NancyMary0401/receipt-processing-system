#!/usr/bin/env python3
"""
Test script for the Receipt OCR Processing System API
This script demonstrates how to use all the API endpoints
"""

import requests
import json
import time
import os
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"

def test_api():
    """Test all API endpoints"""
    print("🧪 Testing Receipt OCR Processing System API")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("\n1. Testing server connection...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Server is running")
            print(f"   Response: {response.json()}")
        else:
            print("❌ Server is not responding correctly")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running on http://localhost:8000")
        return
    
    # Test 2: List files (should be empty initially)
    print("\n2. Testing list files endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/files")
        if response.status_code == 200:
            files = response.json()
            print(f"✅ Found {len(files)} uploaded files")
        else:
            print(f"❌ Error listing files: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: List receipts (should be empty initially)
    print("\n3. Testing list receipts endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/receipts")
        if response.status_code == 200:
            receipts = response.json()
            print(f"✅ Found {receipts['total']} processed receipts")
        else:
            print(f"❌ Error listing receipts: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Upload a sample PDF (if available)
    print("\n4. Testing file upload...")
    
    # Check if sample PDF exists
    sample_pdf = "sample_receipt.pdf"
    if os.path.exists(sample_pdf):
        try:
            with open(sample_pdf, 'rb') as f:
                response = requests.post(f"{BASE_URL}/upload", files={'file': f})
            
            if response.status_code == 200:
                file_data = response.json()
                file_id = file_data['id']
                print(f"✅ File uploaded successfully (ID: {file_id})")
                print(f"   File: {file_data['file_name']}")
                print(f"   Path: {file_data['file_path']}")
                
                # Test 5: Validate the uploaded file
                print("\n5. Testing file validation...")
                response = requests.post(f"{BASE_URL}/validate", data={'file_id': file_id})
                
                if response.status_code == 200:
                    validation_data = response.json()
                    print(f"✅ File validation completed")
                    print(f"   Valid: {validation_data['is_valid']}")
                    if validation_data['invalid_reason']:
                        print(f"   Reason: {validation_data['invalid_reason']}")
                    
                    # Test 6: Process the receipt (if valid)
                    if validation_data['is_valid']:
                        print("\n6. Testing receipt processing...")
                        response = requests.post(f"{BASE_URL}/process", data={'file_id': file_id})
                        
                        if response.status_code == 200:
                            receipt_data = response.json()
                            print(f"✅ Receipt processed successfully (ID: {receipt_data['id']})")
                            print(f"   Merchant: {receipt_data['merchant_name']}")
                            print(f"   Amount: ${receipt_data['total_amount']}")
                            print(f"   Date: {receipt_data['purchased_at']}")
                            
                            # Test 7: Get the processed receipt
                            print("\n7. Testing get receipt by ID...")
                            response = requests.get(f"{BASE_URL}/receipts/{receipt_data['id']}")
                            
                            if response.status_code == 200:
                                receipt = response.json()
                                print(f"✅ Retrieved receipt details")
                                print(f"   Items: {receipt['items']}")
                                print(f"   Payment: {receipt['payment_method']}")
                            else:
                                print(f"❌ Error retrieving receipt: {response.status_code}")
                        else:
                            print(f"❌ Error processing receipt: {response.status_code}")
                            print(f"   Response: {response.text}")
                    else:
                        print("⚠️  Skipping processing - file is not valid")
                else:
                    print(f"❌ Error validating file: {response.status_code}")
            else:
                print(f"❌ Error uploading file: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error during upload test: {e}")
    else:
        print(f"⚠️  Sample PDF file '{sample_pdf}' not found. Skipping upload test.")
        print("   To test upload functionality, place a PDF file named 'sample_receipt.pdf' in the current directory.")
    
    # Test 8: Final list of receipts
    print("\n8. Final receipt count...")
    try:
        response = requests.get(f"{BASE_URL}/receipts")
        if response.status_code == 200:
            receipts = response.json()
            print(f"✅ Total receipts in database: {receipts['total']}")
            if receipts['receipts']:
                print("   Recent receipts:")
                for receipt in receipts['receipts'][-3:]:  # Show last 3
                    print(f"   - ID {receipt['id']}: {receipt['merchant_name']} - ${receipt['total_amount']}")
        else:
            print(f"❌ Error listing receipts: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API testing completed!")
    print("\nTo explore the API interactively, visit:")
    print(f"   📖 Interactive docs: {BASE_URL}/docs")
    print(f"   📚 Alternative docs: {BASE_URL}/redoc")

def create_sample_pdf():
    """Create a simple sample PDF for testing"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        filename = "sample_receipt.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Add receipt content
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "WALMART")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, "Receipt #12345")
        c.drawString(50, height - 100, "Date: 11/15/2023")
        c.drawString(50, height - 120, "Cashier: John Doe")
        
        c.drawString(50, height - 160, "Milk                    $3.99")
        c.drawString(50, height - 180, "Bread                   $2.49")
        c.drawString(50, height - 200, "Eggs                    $4.99")
        
        c.drawString(50, height - 240, "Subtotal:              $11.47")
        c.drawString(50, height - 260, "Tax:                   $0.92")
        c.drawString(50, height - 280, "Total:                 $12.39")
        
        c.drawString(50, height - 320, "Payment: CREDIT")
        
        c.save()
        print(f"✅ Created sample PDF: {filename}")
        return True
    except ImportError:
        print("⚠️  reportlab not available. Cannot create sample PDF.")
        return False
    except Exception as e:
        print(f"❌ Error creating sample PDF: {e}")
        return False

if __name__ == "__main__":
    # Try to create a sample PDF if it doesn't exist
    if not os.path.exists("sample_receipt.pdf"):
        print("📄 Creating sample receipt PDF for testing...")
        create_sample_pdf()
    
    # Run the API tests
    test_api() 