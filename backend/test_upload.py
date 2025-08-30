#!/usr/bin/env python3
"""
Test script to verify upload functionality works end-to-end
"""

import requests
import pandas as pd
import io
import json

# Create a simple test Excel file
def create_test_excel():
    data = {
        'Product Name': ['Test Product 1', 'Test Product 2', 'Test Product 3'],
        'Sales Volume': [100, 200, 150],
        'EAN': ['1234567890123', '2234567890123', '3234567890123'],
        'Date': ['2025-08-01', '2025-08-02', '2025-08-03']
    }
    df = pd.DataFrame(data)
    
    # Save to Excel bytes
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, sheet_name='Demo_Data', index=False, engine='openpyxl')
    excel_buffer.seek(0)
    return excel_buffer.getvalue()

def test_upload():
    # Step 1: Login to get token
    print("🔐 Step 1: Logging in...")
    login_data = {
        "email": "user@email.com",
        "password": "password"
    }
    
    login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
    print(f"Login Status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return False
        
    login_result = login_response.json()
    token = login_result.get("access_token")
    print(f"✅ Login successful, token: {token[:20]}...")
    
    # Step 2: Upload file
    print("\n📁 Step 2: Uploading test file...")
    excel_data = create_test_excel()
    
    files = {
        'file': ('Demo_ReportPeriod04-2025.xlsx', excel_data, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    }
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    upload_response = requests.post("http://localhost:8000/api/upload/", files=files, headers=headers)
    print(f"Upload Status: {upload_response.status_code}")
    
    if upload_response.status_code == 200:
        upload_result = upload_response.json()
        print(f"✅ Upload successful!")
        print(f"Upload ID: {upload_result.get('id')}")
        print(f"Status: {upload_result.get('status')}")
        return upload_result.get('id')
    else:
        print(f"❌ Upload failed: {upload_response.text}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Upload Functionality")
    print("=" * 40)
    upload_id = test_upload()
    
    if upload_id:
        print(f"\n🎉 Test completed successfully! Upload ID: {upload_id}")
        print("Background processing should now be inserting data into mock_data table...")
    else:
        print("\n❌ Test failed!")