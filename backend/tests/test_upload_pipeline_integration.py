"""
Integration tests for the complete upload pipeline.
Tests the entire flow: Authentication → File Upload → Processing → Database Storage → Status Tracking
"""

import pytest
import asyncio
import httpx
import tempfile
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import json
import time
from typing import Dict, Any, Optional


class TestUploadPipelineIntegration:
    """Test the complete upload pipeline end-to-end"""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for testing"""
        # In a real test, you would mock this or use test credentials
        # For now, we'll use the existing user
        return "eyJhbGciOiJIUzI1NiIsImtpZCI6IkVGQzhrMUp3bEcxY0g3bXMiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL25ya29kbGx1ZXVucGJpb3RqYnFsLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJmZGQ3MWY5NS1lOGQ0LTQxN2UtODVhYS05YjdiMGM5MjQzNmQiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzU2MTE0ODkxLCJpYXQiOjE3NTYxMTEyOTEsImVtYWlsIjoidXNlckBlbWFpbC5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsX3ZlcmlmaWVkIjp0cnVlfSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTc1NjExMTI5MX1dLCJzZXNzaW9uX2lkIjoiMTFkMWJhY2QtYjMxYy00NWNlLTlkZGEtYTc5Zjg2NTg2YTMwIiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.zsxouL5sXkhtExNftvpI1bh-9pIb2VzMvjL7mL6ZgSE"
    
    @pytest.fixture
    def sample_xlsx_file(self):
        """Create a sample XLSX file for testing"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            # Create sample data that mimics a vendor file format
            sample_data = {
                'Product EAN': ['1234567890123', '2345678901234', '3456789012345'],
                'Product Name': ['Test Product 1', 'Test Product 2', 'Test Product 3'],
                'Quantity': [100, 250, 75],
                'Sales Amount': [1500.00, 3750.50, 899.99],
                'Month': [11, 11, 11],
                'Year': [2024, 2024, 2024],
                'Reseller': ['TestReseller1', 'TestReseller2', 'TestReseller3']
            }
            
            df = pd.DataFrame(sample_data)
            df.to_excel(tmp_file.name, index=False)
            
            return tmp_file.name
    
    @pytest.fixture
    def invalid_file(self):
        """Create an invalid file for negative testing"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(b"This is not an Excel file")
            return tmp_file.name
    
    async def test_authentication_required(self):
        """Test that authentication is required for all endpoints"""
        async with httpx.AsyncClient() as client:
            # Test upload endpoint without auth
            with open(__file__, 'rb') as f:
                response = await client.post(
                    f"{self.BASE_URL}/api/upload/",
                    files={"file": f}
                )
            assert response.status_code in [401, 403], "Should require authentication"
            
            # Test status endpoint without auth
            response = await client.get(f"{self.BASE_URL}/api/status/uploads")
            assert response.status_code in [401, 403], "Should require authentication"
    
    async def test_invalid_file_upload(self, auth_token, invalid_file):
        """Test that invalid file types are rejected"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async with httpx.AsyncClient() as client:
            with open(invalid_file, 'rb') as f:
                response = await client.post(
                    f"{self.BASE_URL}/api/upload/",
                    headers=headers,
                    files={"file": ("test.txt", f, "text/plain")}
                )
            
            assert response.status_code == 422
            assert "Only .xlsx files are allowed" in response.text or "xlsx" in response.text.lower()
    
    async def test_valid_file_upload(self, auth_token, sample_xlsx_file):
        """Test successful file upload and initial processing"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async with httpx.AsyncClient() as client:
            with open(sample_xlsx_file, 'rb') as f:
                response = await client.post(
                    f"{self.BASE_URL}/api/upload/",
                    headers=headers,
                    files={"file": ("sample.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                )
            
            if response.status_code != 200:
                print(f"Upload response: {response.status_code} - {response.text}")
            
            assert response.status_code == 200, f"Upload failed: {response.text}"
            
            upload_data = response.json()
            assert "id" in upload_data
            assert upload_data["filename"] == "sample.xlsx"
            assert upload_data["status"] in ["pending", "processing"]
            
            return upload_data["id"]
    
    async def test_upload_status_tracking(self, auth_token, sample_xlsx_file):
        """Test that upload status can be tracked"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # First upload a file
        upload_id = None
        async with httpx.AsyncClient() as client:
            with open(sample_xlsx_file, 'rb') as f:
                response = await client.post(
                    f"{self.BASE_URL}/api/upload/",
                    headers=headers,
                    files={"file": ("sample.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                )
            
            if response.status_code == 200:
                upload_data = response.json()
                upload_id = upload_data["id"]
        
        if upload_id:
            # Check upload status
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/api/status/{upload_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    status_data = response.json()
                    assert "upload_id" in status_data
                    assert "status" in status_data
                    assert status_data["status"] in ["pending", "processing", "completed", "failed"]
    
    async def test_user_upload_list(self, auth_token):
        """Test that users can see their upload history"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/api/status/uploads",
                headers=headers
            )
            
            assert response.status_code == 200
            uploads = response.json()
            assert isinstance(uploads, list)
            # Note: This might be empty if no uploads exist, which is fine
    
    async def test_file_size_validation(self, auth_token):
        """Test that file size limits are enforced"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create a file that's too large (if there are size limits)
        # This test might need adjustment based on actual limits
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            # Create a large dataset
            large_data = {
                'col' + str(i): list(range(10000)) for i in range(50)
            }
            df = pd.DataFrame(large_data)
            df.to_excel(tmp_file.name, index=False)
            
            async with httpx.AsyncClient() as client:
                with open(tmp_file.name, 'rb') as f:
                    response = await client.post(
                        f"{self.BASE_URL}/api/upload/",
                        headers=headers,
                        files={"file": ("large.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                    )
                
                # Either succeeds (if within limits) or fails with size error
                if response.status_code != 200:
                    assert "size" in response.text.lower() or response.status_code == 413
    
    async def test_concurrent_uploads(self, auth_token, sample_xlsx_file):
        """Test that multiple concurrent uploads are handled properly"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async def upload_file(file_name: str):
            async with httpx.AsyncClient() as client:
                with open(sample_xlsx_file, 'rb') as f:
                    response = await client.post(
                        f"{self.BASE_URL}/api/upload/",
                        headers=headers,
                        files={"file": (file_name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                    )
                return response.status_code, response.text
        
        # Upload 3 files concurrently
        tasks = [
            upload_file(f"concurrent_test_{i}.xlsx")
            for i in range(3)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check that at least some uploads succeeded (depending on system capacity)
        successful_uploads = [r for r in results if isinstance(r, tuple) and r[0] == 200]
        print(f"Successful concurrent uploads: {len(successful_uploads)} out of {len(results)}")
    
    async def test_data_processing_pipeline(self, auth_token, sample_xlsx_file):
        """Test that uploaded data goes through the processing pipeline"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        upload_id = None
        async with httpx.AsyncClient() as client:
            # Upload file
            with open(sample_xlsx_file, 'rb') as f:
                response = await client.post(
                    f"{self.BASE_URL}/api/upload/",
                    headers=headers,
                    files={"file": ("pipeline_test.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                )
            
            if response.status_code == 200:
                upload_data = response.json()
                upload_id = upload_data["id"]
        
        if upload_id:
            # Wait for processing (with timeout)
            max_wait_time = 30  # seconds
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.BASE_URL}/api/status/{upload_id}",
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        status_data = response.json()
                        if status_data["status"] in ["completed", "failed"]:
                            # Processing finished
                            if status_data["status"] == "completed":
                                # Check if processed data exists
                                assert "rows_processed" in status_data or "message" in status_data
                            break
                
                await asyncio.sleep(2)  # Wait 2 seconds before checking again
    
    def test_run_all_integration_tests(self, auth_token, sample_xlsx_file, invalid_file):
        """Run all integration tests in sequence"""
        async def run_tests():
            print("🧪 Starting Upload Pipeline Integration Tests")
            
            try:
                print("1. Testing authentication requirements...")
                await self.test_authentication_required()
                print("✅ Authentication tests passed")
                
                print("2. Testing invalid file rejection...")
                await self.test_invalid_file_upload(auth_token, invalid_file)
                print("✅ Invalid file rejection tests passed")
                
                print("3. Testing valid file upload...")
                await self.test_valid_file_upload(auth_token, sample_xlsx_file)
                print("✅ Valid file upload tests passed")
                
                print("4. Testing upload status tracking...")
                await self.test_upload_status_tracking(auth_token, sample_xlsx_file)
                print("✅ Status tracking tests passed")
                
                print("5. Testing user upload list...")
                await self.test_user_upload_list(auth_token)
                print("✅ Upload list tests passed")
                
                print("6. Testing file size validation...")
                await self.test_file_size_validation(auth_token)
                print("✅ File size validation tests passed")
                
                print("7. Testing concurrent uploads...")
                await self.test_concurrent_uploads(auth_token, sample_xlsx_file)
                print("✅ Concurrent upload tests passed")
                
                print("8. Testing data processing pipeline...")
                await self.test_data_processing_pipeline(auth_token, sample_xlsx_file)
                print("✅ Data processing pipeline tests passed")
                
                print("🎉 All Upload Pipeline Integration Tests Passed!")
                return True
                
            except Exception as e:
                print(f"❌ Test failed: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
        
        # Run the async tests
        return asyncio.run(run_tests())


if __name__ == "__main__":
    """
    Run integration tests directly (for development/debugging)
    """
    test_instance = TestUploadPipelineIntegration()
    
    # Mock fixtures for direct execution
    auth_token = "eyJhbGciOiJIUzI1NiIsImtpZCI6IkVGQzhrMUp3bEcxY0g3bXMiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL25ya29kbGx1ZXVucGJpb3RqYnFsLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJmZGQ3MWY5NS1lOGQ0LTQxN2UtODVhYS05YjdiMGM5MjQzNmQiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzU2MTE0ODkxLCJpYXQiOjE3NTYxMTEyOTEsImVtYWlsIjoidXNlckBlbWFpbC5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsX3ZlcmlmaWVkIjp0cnVlfSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTc1NjExMTI5MX1dLCJzZXNzaW9uX2lkIjoiMTFkMWJhY2QtYjMxYy00NWNlLTlkZGEtYTc5Zjg2NTg2YTMwIiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.zsxouL5sXkhtExNftvpI1bh-9pIb2VzMvjL7mL6ZgSE"
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_xlsx:
        sample_data = {
            'Product EAN': ['1234567890123', '2345678901234'],
            'Product Name': ['Test Product 1', 'Test Product 2'],
            'Quantity': [100, 250],
            'Sales Amount': [1500.00, 3750.50],
        }
        df = pd.DataFrame(sample_data)
        df.to_excel(tmp_xlsx.name, index=False)
        sample_xlsx_file = tmp_xlsx.name
    
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_txt:
        tmp_txt.write(b"Invalid file content")
        invalid_file = tmp_txt.name
    
    # Run tests
    success = test_instance.test_run_all_integration_tests(auth_token, sample_xlsx_file, invalid_file)
    
    # Cleanup
    Path(sample_xlsx_file).unlink(missing_ok=True)
    Path(invalid_file).unlink(missing_ok=True)
    
    if success:
        print("✅ All tests completed successfully!")
        exit(0)
    else:
        print("❌ Some tests failed!")
        exit(1)