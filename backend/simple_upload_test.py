#!/usr/bin/env python3
"""
Simple upload test to check if basic functionality works
"""

import requests
import pandas as pd
import tempfile
import os

def simple_test():
    base_url = "http://localhost:8000/api"
    
    print("🧪 Simple Upload Test")
    print("=" * 30)
    
    # Login
    print("1. Login...")
    try:
        login_response = requests.post(f"{base_url}/auth/login", 
                                     json={"email": "test2@example.com", "password": "testpassword123"},
                                     timeout=10)
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            print(f"✅ Login OK")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return
    
    # Create simple test file
    print("2. Create file...")
    test_data = {'Product EAN': [1234567890123], 'Month': [5], 'Year': [2024], 'Quantity': [1]}
    df = pd.DataFrame(test_data)
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
        excel_file_path = tmp_file.name
        df.to_excel(excel_file_path, index=False)
    
    print(f"✅ File created")
    
    # Upload
    print("3. Upload...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        with open(excel_file_path, 'rb') as file:
            files = {'file': ('simple_test.xlsx', file)}
            upload_response = requests.post(f"{base_url}/upload/", 
                                          files=files, 
                                          headers=headers,
                                          timeout=15)
        
        if upload_response.status_code == 200:
            upload_result = upload_response.json()
            upload_id = upload_result.get('id')
            print(f"✅ Upload OK: {upload_id}")
        else:
            print(f"❌ Upload failed: {upload_response.status_code}")
            print(f"Response: {upload_response.text}")
    
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
    finally:
        os.remove(excel_file_path)
    
    print("Done!")

if __name__ == "__main__":
    simple_test()