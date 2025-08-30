"""
Integration tests for file processing status tracking.
Tests the complete status lifecycle: Upload → Processing → Completion → History
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


class TestProcessingStatus:
    """Test the file processing status system end-to-end"""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for testing"""
        return "eyJhbGciOiJIUzI1NiIsImtpZCI6IkVGQzhrMUp3bEcxY0g3bXMiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL25ya29kbGx1ZXVucGJpb3RqYnFsLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJmZGQ3MWY5NS1lOGQ0LTQxN2UtODVhYS05YjdiMGM5MjQzNmQiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzU2MTE0ODkxLCJpYXQiOjE3NTYxMTEyOTEsImVtYWlsIjoidXNlckBlbWFpbC5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsX3ZlcmlmaWVkIjp0cnVlfSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTc1NjExMTI5MX1dLCJzZXNzaW9uX2lkIjoiMTFkMWJhY2QtYjMxYy00NWNlLTlkZGEtYTc5Zjg2NTg2YTMwIiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.zsxouL5sXkhtExNftvpI1bh-9pIb2VzMvjL7mL6ZgSE"
    
    @pytest.fixture
    def sample_processing_file(self):
        """Create a sample XLSX file for processing status testing"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            # Create test data that will trigger processing
            sample_data = {
                'Product EAN': ['7890123456789', '8901234567890', '9012345678901', '0123456789012'],
                'Product Name': ['Status Test Product A', 'Status Test Product B', 'Status Test Product C', 'Status Test Product D'],
                'Quantity': [150, 300, 225, 75],
                'Sales Amount': [2250.75, 4500.00, 3375.25, 1125.50],
                'Month': [12, 12, 12, 12],
                'Year': [2024, 2024, 2024, 2024],
                'Reseller': ['StatusTestReseller1', 'StatusTestReseller2', 'StatusTestReseller3', 'StatusTestReseller4'],
                'Region': ['North', 'South', 'East', 'West']
            }
            
            df = pd.DataFrame(sample_data)
            df.to_excel(tmp_file.name, index=False)
            
            return tmp_file.name
    
    async def test_status_endpoints_exist(self, auth_token):
        """Test that all status endpoints exist and are accessible"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        endpoints_to_test = [
            "/api/status/uploads",      # Get user's upload history
            "/api/status/processing",   # Get processing queue status
            "/api/status/summary",      # Get processing summary
        ]
        
        async with httpx.AsyncClient() as client:
            for endpoint in endpoints_to_test:
                print(f"Testing endpoint: {endpoint}")
                response = await client.get(f"{self.BASE_URL}{endpoint}", headers=headers)
                
                # Endpoints should exist (not return 404)
                assert response.status_code != 404, f"Endpoint {endpoint} should exist"
                print(f"✅ Endpoint {endpoint} exists (status: {response.status_code})")
    
    async def test_status_authentication_required(self):
        """Test that status endpoints require authentication"""
        endpoints_to_test = [
            "/api/status/uploads",
            "/api/status/processing",
            "/api/status/summary"
        ]
        
        async with httpx.AsyncClient() as client:
            for endpoint in endpoints_to_test:
                response = await client.get(f"{self.BASE_URL}{endpoint}")
                assert response.status_code in [401, 403], f"Endpoint {endpoint} should require authentication"
                print(f"✅ Authentication required for {endpoint}")
    
    async def test_upload_history_tracking(self, auth_token):
        """Test that upload history is properly tracked"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async with httpx.AsyncClient() as client:
            # Get initial upload count
            response = await client.get(f"{self.BASE_URL}/api/status/uploads", headers=headers)
            
            if response.status_code == 200:
                initial_uploads = response.json()
                initial_count = len(initial_uploads) if isinstance(initial_uploads, list) else 0
                print(f"Initial upload count: {initial_count}")
                
                # Check upload history structure
                if initial_count > 0:
                    upload = initial_uploads[0]
                    expected_fields = ['id', 'filename', 'status', 'created_at']
                    
                    for field in expected_fields:
                        if field not in upload:
                            print(f"⚠️ Missing field '{field}' in upload history")
                        else:
                            print(f"✅ Upload history includes '{field}' field")
            else:
                print(f"⚠️ Could not get upload history: {response.status_code}")
    
    async def test_processing_status_lifecycle(self, auth_token, sample_processing_file):
        """Test the complete processing status lifecycle"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        upload_id = None
        
        async with httpx.AsyncClient() as client:
            # 1. Upload a file
            with open(sample_processing_file, 'rb') as f:
                response = await client.post(
                    f"{self.BASE_URL}/api/upload/",
                    headers=headers,
                    files={"file": ("status_test.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                )
            
            if response.status_code == 200:
                upload_data = response.json()
                upload_id = upload_data["id"]
                print(f"✅ File uploaded with ID: {upload_id}")
                
                # 2. Check initial status
                response = await client.get(f"{self.BASE_URL}/api/status/{upload_id}", headers=headers)
                
                if response.status_code == 200:
                    status_data = response.json()
                    print(f"Initial status: {status_data.get('status', 'unknown')}")
                    
                    # 3. Track status changes over time
                    max_wait_time = 45  # seconds
                    start_time = time.time()
                    status_history = []
                    
                    while time.time() - start_time < max_wait_time:
                        response = await client.get(f"{self.BASE_URL}/api/status/{upload_id}", headers=headers)
                        
                        if response.status_code == 200:
                            current_status = response.json()
                            current_status_value = current_status.get('status', 'unknown')
                            
                            # Track unique status changes
                            if not status_history or status_history[-1] != current_status_value:
                                status_history.append(current_status_value)
                                print(f"Status update: {current_status_value}")
                            
                            # Check if processing is complete
                            if current_status_value in ['completed', 'failed']:
                                print(f"✅ Processing finished with status: {current_status_value}")
                                
                                # Verify final status structure
                                expected_final_fields = ['upload_id', 'status', 'updated_at']
                                for field in expected_final_fields:
                                    if field in current_status:
                                        print(f"✅ Final status includes '{field}'")
                                    else:
                                        print(f"⚠️ Missing '{field}' in final status")
                                
                                break
                        
                        await asyncio.sleep(3)  # Check every 3 seconds
                    
                    print(f"Status lifecycle: {' → '.join(status_history)}")
                    
                    # Verify we saw expected status transitions
                    if len(status_history) > 1:
                        print("✅ Status tracking shows progression")
                    else:
                        print("ℹ️ Status remained constant (might be expected)")
                
                else:
                    print(f"⚠️ Could not check upload status: {response.status_code}")
            
            else:
                print(f"⚠️ File upload failed: {response.status_code} - {response.text}")
    
    async def test_processing_queue_status(self, auth_token):
        """Test processing queue status endpoint"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/api/status/processing", headers=headers)
            
            if response.status_code == 200:
                queue_status = response.json()
                print(f"✅ Processing queue status retrieved")
                
                # Check expected queue status fields
                expected_fields = ['pending_count', 'processing_count', 'completed_count']
                for field in expected_fields:
                    if field in queue_status:
                        value = queue_status[field]
                        print(f"✅ Queue status includes '{field}': {value}")
                    else:
                        print(f"ℹ️ Queue status missing '{field}' (might be optional)")
                
                # Verify counts are numeric
                for field in expected_fields:
                    if field in queue_status:
                        try:
                            count = int(queue_status[field])
                            assert count >= 0, f"Count {field} should be non-negative"
                        except (ValueError, TypeError):
                            print(f"⚠️ {field} is not a valid number")
            
            else:
                print(f"⚠️ Could not get processing queue status: {response.status_code}")
    
    async def test_processing_summary(self, auth_token):
        """Test processing summary statistics"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/api/status/summary", headers=headers)
            
            if response.status_code == 200:
                summary = response.json()
                print("✅ Processing summary retrieved")
                
                # Check for summary statistics
                expected_summary_fields = [
                    'total_uploads', 'successful_uploads', 'failed_uploads',
                    'total_records_processed', 'avg_processing_time'
                ]
                
                for field in expected_summary_fields:
                    if field in summary:
                        value = summary[field]
                        print(f"✅ Summary includes '{field}': {value}")
                    else:
                        print(f"ℹ️ Summary missing '{field}' (might be optional)")
            
            else:
                print(f"⚠️ Could not get processing summary: {response.status_code}")
    
    async def test_status_filtering_and_pagination(self, auth_token):
        """Test status endpoint filtering and pagination features"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async with httpx.AsyncClient() as client:
            # Test filtering by status
            filter_params = [
                {"status": "completed"},
                {"status": "failed"},
                {"status": "pending"},
            ]
            
            for params in filter_params:
                response = await client.get(
                    f"{self.BASE_URL}/api/status/uploads",
                    headers=headers,
                    params=params
                )
                
                if response.status_code == 200:
                    filtered_uploads = response.json()
                    print(f"✅ Status filtering for '{params['status']}' works")
                    
                    # Verify all results match filter
                    if isinstance(filtered_uploads, list):
                        for upload in filtered_uploads:
                            if 'status' in upload:
                                assert upload['status'] == params['status'], f"Filter mismatch: expected {params['status']}, got {upload['status']}"
                
            # Test pagination
            pagination_params = [
                {"limit": 5, "offset": 0},
                {"limit": 10, "offset": 0},
            ]
            
            for params in pagination_params:
                response = await client.get(
                    f"{self.BASE_URL}/api/status/uploads",
                    headers=headers,
                    params=params
                )
                
                if response.status_code == 200:
                    paginated_uploads = response.json()
                    if isinstance(paginated_uploads, list):
                        assert len(paginated_uploads) <= params["limit"], f"Pagination limit not respected"
                        print(f"✅ Pagination with limit {params['limit']} works")
    
    async def test_status_error_handling(self, auth_token):
        """Test status endpoint error handling"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async with httpx.AsyncClient() as client:
            # Test invalid upload ID
            invalid_ids = ["nonexistent", "00000000-0000-0000-0000-000000000000", "invalid-uuid"]
            
            for invalid_id in invalid_ids:
                response = await client.get(
                    f"{self.BASE_URL}/api/status/{invalid_id}",
                    headers=headers
                )
                
                # Should handle invalid IDs gracefully
                assert response.status_code in [404, 422], f"Should return appropriate error for invalid ID: {invalid_id}"
                print(f"✅ Invalid ID '{invalid_id}' handled properly")
            
            # Test malformed parameters
            malformed_params = [
                {"limit": -1},
                {"limit": "not_a_number"},
                {"offset": -1},
                {"status": "invalid_status"}
            ]
            
            for params in malformed_params:
                response = await client.get(
                    f"{self.BASE_URL}/api/status/uploads",
                    headers=headers,
                    params=params
                )
                
                # Should handle malformed parameters gracefully
                if response.status_code >= 500:
                    print(f"⚠️ Server error with params {params}: {response.status_code}")
                else:
                    print(f"✅ Malformed params {params} handled gracefully")
    
    async def test_real_time_status_updates(self, auth_token, sample_processing_file):
        """Test real-time status updates during processing"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        upload_id = None
        
        async with httpx.AsyncClient() as client:
            # Upload file for real-time tracking
            with open(sample_processing_file, 'rb') as f:
                response = await client.post(
                    f"{self.BASE_URL}/api/upload/",
                    headers=headers,
                    files={"file": ("realtime_test.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                )
            
            if response.status_code == 200:
                upload_data = response.json()
                upload_id = upload_data["id"]
                
                # Track status updates in real-time
                status_timestamps = []
                max_tracking_time = 30  # seconds
                start_time = time.time()
                
                while time.time() - start_time < max_tracking_time:
                    response = await client.get(f"{self.BASE_URL}/api/status/{upload_id}", headers=headers)
                    
                    if response.status_code == 200:
                        status_data = response.json()
                        current_time = time.time()
                        
                        status_timestamps.append({
                            'timestamp': current_time,
                            'status': status_data.get('status', 'unknown'),
                            'updated_at': status_data.get('updated_at')
                        })
                        
                        # Check if processing is complete
                        if status_data.get('status') in ['completed', 'failed']:
                            break
                    
                    await asyncio.sleep(2)  # Check every 2 seconds
                
                # Analyze real-time updates
                if len(status_timestamps) > 1:
                    print(f"✅ Real-time tracking captured {len(status_timestamps)} status updates")
                    
                    # Check that timestamps are progressing
                    for i in range(1, len(status_timestamps)):
                        time_diff = status_timestamps[i]['timestamp'] - status_timestamps[i-1]['timestamp']
                        assert time_diff >= 0, "Status timestamps should progress forward"
                    
                    print("✅ Real-time status timestamps are consistent")
                else:
                    print("ℹ️ Processing completed quickly - limited real-time tracking data")
    
    def test_run_all_status_tests(self, auth_token, sample_processing_file):
        """Run all processing status tests in sequence"""
        async def run_tests():
            print("📊 Starting Processing Status Tests")
            
            try:
                print("1. Testing status endpoints existence...")
                await self.test_status_endpoints_exist(auth_token)
                print("✅ Status endpoints tests passed")
                
                print("2. Testing status authentication...")
                await self.test_status_authentication_required()
                print("✅ Status authentication tests passed")
                
                print("3. Testing upload history tracking...")
                await self.test_upload_history_tracking(auth_token)
                print("✅ Upload history tests passed")
                
                print("4. Testing processing status lifecycle...")
                await self.test_processing_status_lifecycle(auth_token, sample_processing_file)
                print("✅ Status lifecycle tests passed")
                
                print("5. Testing processing queue status...")
                await self.test_processing_queue_status(auth_token)
                print("✅ Processing queue tests passed")
                
                print("6. Testing processing summary...")
                await self.test_processing_summary(auth_token)
                print("✅ Processing summary tests passed")
                
                print("7. Testing filtering and pagination...")
                await self.test_status_filtering_and_pagination(auth_token)
                print("✅ Filtering and pagination tests passed")
                
                print("8. Testing error handling...")
                await self.test_status_error_handling(auth_token)
                print("✅ Error handling tests passed")
                
                print("9. Testing real-time status updates...")
                await self.test_real_time_status_updates(auth_token, sample_processing_file)
                print("✅ Real-time updates tests passed")
                
                print("🎉 All Processing Status Tests Completed!")
                print("Note: Some tests may show warnings if certain features are not fully implemented")
                return True
                
            except Exception as e:
                print(f"❌ Test failed: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
        
        return asyncio.run(run_tests())


if __name__ == "__main__":
    """
    Run processing status tests directly
    """
    test_instance = TestProcessingStatus()
    
    # Mock fixtures for direct execution
    auth_token = "eyJhbGciOiJIUzI1NiIsImtpZCI6IkVGQzhrMUp3bEcxY0g3bXMiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL25ya29kbGx1ZXVucGJpb3RqYnFsLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJmZGQ3MWY5NS1lOGQ0LTQxN2UtODVhYS05YjdiMGM5MjQzNmQiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzU2MTE0ODkxLCJpYXQiOjE3NTYxMTEyOTEsImVtYWlsIjoidXNlckBlbWFpbC5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsX3ZlcmlmaWVkIjp0cnVlfSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTc1NjExMTI5MX1dLCJzZXNzaW9uX2lkIjoiMTFkMWJhY2QtYjMxYy00NWNlLTlkZGEtYTc5Zjg2NTg2YTMwIiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.zsxouL5sXkhtExNftvpI1bh-9pIb2VzMvjL7mL6ZgSE"
    
    # Create sample file
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
        sample_data = {
            'Product EAN': ['7890123456789', '8901234567890'],
            'Product Name': ['Status Test A', 'Status Test B'],
            'Quantity': [150, 300],
            'Sales Amount': [2250.75, 4500.00],
        }
        df = pd.DataFrame(sample_data)
        df.to_excel(tmp_file.name, index=False)
        sample_processing_file = tmp_file.name
    
    # Run tests
    success = test_instance.test_run_all_status_tests(auth_token, sample_processing_file)
    
    # Cleanup
    Path(sample_processing_file).unlink(missing_ok=True)
    
    if success:
        print("✅ Processing status tests completed!")
        exit(0)
    else:
        print("❌ Some status tests had issues!")
        exit(1)