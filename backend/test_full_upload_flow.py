#!/usr/bin/env python3
"""
Test the complete upload flow with the new hybrid configuration
This should now insert data into the actual Supabase mock_data table
"""

import requests
import pandas as pd
import tempfile
import time
import os
import asyncio

def test_upload_to_supabase():
    """Test complete upload flow to Supabase"""
    base_url = "http://localhost:8000/api"
    
    print("🚀 Testing Complete Upload Flow to Supabase")
    print("=" * 60)
    
    # Step 1: Login
    print("1. 🔐 Authenticating...")
    login_data = {"email": "test@example.com", "password": "testpassword123"}
    login_response = requests.post(f"{base_url}/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
        
    token = login_response.json().get("access_token")
    print(f"✅ Login successful")
    
    # Step 2: Create test Excel data 
    print("\n2. 📁 Creating test Excel file...")
    test_data = {
        'Product EAN': ['9999888877776'],
        'Month': [4],
        'Year': [2024], 
        'Quantity': [15],
        'Sales LC': [30.00],
        'Sales EUR': [27.00],
        'Currency': ['EUR'],
        'Reseller': ['Supabase Test'],
        'Functional Name': ['Supabase Test Product']
    }
    
    df = pd.DataFrame(test_data)
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
        excel_file_path = tmp_file.name
        df.to_excel(excel_file_path, index=False, sheet_name='TestData')
    
    print(f"✅ Created test file with 1 row")
    
    # Step 3: Upload file
    print("\n3. 📤 Uploading file...")
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(excel_file_path, 'rb') as file:
        files = {'file': ('supabase_test.xlsx', file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        upload_response = requests.post(f"{base_url}/upload/", files=files, headers=headers)
    
    # Clean up temp file
    os.remove(excel_file_path)
    
    if upload_response.status_code == 200:
        upload_result = upload_response.json()
        upload_id = upload_result.get('id')
        print(f"✅ Upload successful")
        print(f"   Upload ID: {upload_id}")
    else:
        print(f"❌ Upload failed: {upload_response.status_code} - {upload_response.text}")
        return False
    
    # Step 4: Wait for processing
    print("\n4. ⏳ Waiting for background processing...")
    time.sleep(8)  # Give it time to process
    
    # Step 5: Check upload status
    print("\n5. 📊 Checking upload status...")
    status_response = requests.get(f"{base_url}/status/{upload_id}", headers=headers)
    
    if status_response.status_code == 200:
        status_data = status_response.json()
        print(f"✅ Status retrieved: {status_data.get('status')}")
        if status_data.get('message'):
            print(f"   Message: {status_data.get('message')}")
        print(f"   Rows processed: {status_data.get('rows_processed', 0)}")
    else:
        print(f"⚠️  Status check failed: {status_response.status_code}")
        if status_response.status_code == 404:
            print("   This might mean the upload record isn't in Supabase uploads table")
    
    # Step 6: Check user uploads list
    print("\n6. 📝 Checking uploads list...")
    uploads_response = requests.get(f"{base_url}/status/uploads", headers=headers)
    
    if uploads_response.status_code == 200:
        uploads = uploads_response.json()
        print(f"✅ Retrieved {len(uploads)} uploads")
        if uploads:
            latest_upload = uploads[0]
            print(f"   Latest upload: {latest_upload.get('filename')} - {latest_upload.get('status')}")
    else:
        print(f"⚠️  Uploads list failed: {uploads_response.status_code}")
    
    print(f"\n🎯 Upload ID for verification: {upload_id}")
    print("   Check this upload_id in the Supabase mock_data table")
    
    return True

def main():
    print("🧪 Testing Upload Flow with Supabase Database Integration")
    print("This should now store data in the actual Supabase mock_data table")
    print("=" * 70)
    
    success = test_upload_to_supabase()
    
    print("\n" + "=" * 70)
    print("📊 UPLOAD TEST SUMMARY")  
    print("=" * 70)
    print(f"Upload Flow Test: {'✅ PASS' if success else '❌ FAIL'}")
    
    if success:
        print("\n🎉 Upload flow completed!")
        print("   Check the Supabase mock_data table for the processed data")
        print("   Look for entries with the upload_id shown above")
    else:
        print("\n⚠️  Upload flow had issues - check the detailed output above")

if __name__ == "__main__":
    main()