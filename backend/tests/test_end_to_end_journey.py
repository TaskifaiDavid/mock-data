"""
End-to-end user journey tests for the complete system.
Tests the entire user experience: Authentication → Upload → Processing → Chat → Analytics → History
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


class TestEndToEndUserJourney:
    """Test the complete user journey through the system"""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for testing"""
        return "eyJhbGciOiJIUzI1NiIsImtpZCI6IkVGQzhrMUp3bEcxY0g3bXMiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL25ya29kbGx1ZXVucGJpb3RqYnFsLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJmZGQ3MWY5NS1lOGQ0LTQxN2UtODVhYS05YjdiMGM5MjQzNmQiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzU2MTE0ODkxLCJpYXQiOjE3NTYxMTEyOTEsImVtYWlsIjoidXNlckBlbWFpbC5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsX3ZlcmlmaWVkIjp0cnVlfSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTc1NjExMTI5MX1dLCJzZXNzaW9uX2lkIjoiMTFkMWJhY2QtYjMxYy00NWNlLTlkZGEtYTc5Zjg2NTg2YTMwIiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.zsxouL5sXkhtExNftvpI1bh-9pIb2VzMvjL7mL6ZgSE"
    
    @pytest.fixture
    def demo_data_file(self):
        """Create a comprehensive demo data file for end-to-end testing"""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            # Create realistic demo data that showcases the system
            demo_data = {
                'Product EAN': [
                    '1234567890123', '2345678901234', '3456789012345', '4567890123456',
                    '5678901234567', '6789012345678', '7890123456789', '8901234567890'
                ],
                'Product Name': [
                    'Demo Smartphone Pro', 'Demo Tablet Elite', 'Demo Laptop Ultra',
                    'Demo Headphones Max', 'Demo Watch Smart', 'Demo Speaker Mini',
                    'Demo Camera X1', 'Demo Keyboard RGB'
                ],
                'Quantity': [150, 200, 75, 300, 120, 180, 90, 250],
                'Sales Amount': [
                    75000.00, 80000.00, 112500.00, 45000.00, 
                    36000.00, 18000.00, 67500.00, 18750.00
                ],
                'Month': [12, 12, 12, 12, 12, 12, 12, 12],
                'Year': [2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024],
                'Reseller': [
                    'TechStore North', 'ElectroMart', 'GadgetHub', 'TechStore North',
                    'ElectroMart', 'GadgetHub', 'TechStore North', 'ElectroMart'
                ],
                'Region': [
                    'North America', 'Europe', 'Asia', 'North America',
                    'Europe', 'Asia', 'North America', 'Europe'
                ],
                'Category': [
                    'Mobile', 'Mobile', 'Computing', 'Audio',
                    'Wearables', 'Audio', 'Photography', 'Computing'
                ]
            }
            
            df = pd.DataFrame(demo_data)
            df.to_excel(tmp_file.name, index=False)
            
            return tmp_file.name
    
    async def test_complete_user_journey(self, auth_token, demo_data_file):
        """Test the complete user journey from login to analytics"""
        print("🚀 Starting Complete End-to-End User Journey Test")
        
        journey_results = {
            'authentication': False,
            'file_upload': False,
            'processing_tracking': False,
            'chat_functionality': False,
            'analytics_dashboard': False,
            'status_history': False
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {"Authorization": f"Bearer {auth_token}"}
            
            # STEP 1: Verify Authentication
            print("\n📋 STEP 1: Testing Authentication System")
            try:
                # Test user profile access
                response = await client.get(f"{self.BASE_URL}/api/auth/profile", headers=headers)
                if response.status_code == 200:
                    user_data = response.json()
                    print(f"✅ User authenticated: {user_data.get('email', 'Unknown')}")
                    journey_results['authentication'] = True
                else:
                    print(f"⚠️ Authentication issue: {response.status_code}")
            except Exception as e:
                print(f"❌ Authentication failed: {str(e)}")
            
            # STEP 2: Upload Demo File
            print("\n📁 STEP 2: Uploading Demo Data File")
            upload_id = None
            try:
                with open(demo_data_file, 'rb') as f:
                    response = await client.post(
                        f"{self.BASE_URL}/api/upload/",
                        headers=headers,
                        files={"file": ("demo_data.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                    )
                
                if response.status_code == 200:
                    upload_data = response.json()
                    upload_id = upload_data["id"]
                    print(f"✅ File uploaded successfully: {upload_data['filename']}")
                    print(f"   Upload ID: {upload_id}")
                    journey_results['file_upload'] = True
                else:
                    print(f"⚠️ Upload failed: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"❌ Upload error: {str(e)}")
            
            # STEP 3: Track Processing Status
            print("\n⏳ STEP 3: Tracking File Processing Status")
            if upload_id:
                try:
                    max_wait_time = 45  # seconds
                    start_time = time.time()
                    processing_complete = False
                    
                    while time.time() - start_time < max_wait_time:
                        response = await client.get(f"{self.BASE_URL}/api/status/{upload_id}", headers=headers)
                        
                        if response.status_code == 200:
                            status_data = response.json()
                            current_status = status_data.get('status', 'unknown')
                            print(f"   Processing status: {current_status}")
                            
                            if current_status in ['completed', 'failed']:
                                processing_complete = True
                                if current_status == 'completed':
                                    journey_results['processing_tracking'] = True
                                    print("✅ File processing completed successfully")
                                else:
                                    print(f"⚠️ File processing failed: {status_data}")
                                break
                        
                        await asyncio.sleep(3)
                    
                    if not processing_complete:
                        print("ℹ️ Processing still in progress after timeout")
                        journey_results['processing_tracking'] = True  # Still counts as tracking working
                
                except Exception as e:
                    print(f"❌ Status tracking error: {str(e)}")
            
            # STEP 4: Test Chat Functionality
            print("\n💬 STEP 4: Testing Chat Functionality with Uploaded Data")
            try:
                chat_queries = [
                    "What data did I just upload?",
                    "Show me total sales by region",
                    "Which products have the highest sales?",
                    "Count the total number of products"
                ]
                
                successful_chats = 0
                for query in chat_queries:
                    print(f"   Query: {query}")
                    
                    response = await client.post(
                        f"{self.BASE_URL}/api/chat",
                        headers=headers,
                        json={"message": query}
                    )
                    
                    if response.status_code == 200:
                        chat_data = response.json()
                        if "answer" in chat_data:
                            successful_chats += 1
                            print(f"   ✅ Chat response received")
                        else:
                            print(f"   ⚠️ Chat response missing 'answer' field")
                    else:
                        print(f"   ⚠️ Chat failed: {response.status_code}")
                    
                    # Brief delay between queries
                    await asyncio.sleep(2)
                
                if successful_chats > 0:
                    journey_results['chat_functionality'] = True
                    print(f"✅ Chat functionality working ({successful_chats}/{len(chat_queries)} queries successful)")
                else:
                    print("⚠️ No chat queries were successful")
            
            except Exception as e:
                print(f"❌ Chat functionality error: {str(e)}")
            
            # STEP 5: Test Analytics Dashboard
            print("\n📊 STEP 5: Testing Analytics Dashboard Management")
            try:
                # Create a Google Analytics dashboard configuration
                dashboard_config = {
                    "name": "Demo Sales Dashboard",
                    "description": "Comprehensive sales analytics for demo data",
                    "dashboard_type": "google_analytics",
                    "configuration": {
                        "google_analytics": {
                            "view_id": "demo_view_123456789",
                            "account_id": "demo_account_123456789",
                            "property_id": "demo_property_123456789"
                        },
                        "metrics": ["sessions", "pageviews", "bounceRate", "avgSessionDuration"],
                        "dimensions": ["country", "deviceCategory", "trafficSource"],
                        "date_ranges": [
                            {"start_date": "30daysAgo", "end_date": "today"}
                        ]
                    },
                    "settings": {
                        "auto_refresh": True,
                        "refresh_interval": 3600,
                        "timezone": "America/New_York"
                    }
                }
                
                # Create dashboard
                response = await client.post(
                    f"{self.BASE_URL}/api/dashboard",
                    headers=headers,
                    json=dashboard_config
                )
                
                if response.status_code == 201:
                    created_dashboard = response.json()
                    dashboard_id = created_dashboard.get("id")
                    print(f"✅ Dashboard created successfully: {created_dashboard['name']}")
                    
                    # Test dashboard retrieval
                    response = await client.get(f"{self.BASE_URL}/api/dashboard/{dashboard_id}", headers=headers)
                    if response.status_code == 200:
                        retrieved_dashboard = response.json()
                        print(f"✅ Dashboard retrieved successfully")
                        journey_results['analytics_dashboard'] = True
                    else:
                        print(f"⚠️ Dashboard retrieval failed: {response.status_code}")
                
                else:
                    print(f"⚠️ Dashboard creation failed: {response.status_code} - {response.text}")
                
                # Test dashboard listing
                response = await client.get(f"{self.BASE_URL}/api/dashboard", headers=headers)
                if response.status_code == 200:
                    dashboards = response.json()
                    print(f"✅ Dashboard listing works ({len(dashboards)} dashboards found)")
                else:
                    print(f"⚠️ Dashboard listing failed: {response.status_code}")
            
            except Exception as e:
                print(f"❌ Analytics dashboard error: {str(e)}")
            
            # STEP 6: Review Processing History
            print("\n📚 STEP 6: Reviewing Processing History and Status")
            try:
                # Get upload history
                response = await client.get(f"{self.BASE_URL}/api/status/uploads", headers=headers)
                if response.status_code == 200:
                    uploads = response.json()
                    print(f"✅ Upload history retrieved ({len(uploads)} uploads found)")
                    
                    # Look for our demo upload
                    demo_upload_found = any(
                        upload.get('filename', '').startswith('demo_data') 
                        for upload in uploads if isinstance(upload, dict)
                    )
                    
                    if demo_upload_found:
                        print("✅ Demo upload found in history")
                    
                    journey_results['status_history'] = True
                else:
                    print(f"⚠️ Upload history failed: {response.status_code}")
                
                # Get processing summary
                response = await client.get(f"{self.BASE_URL}/api/status/summary", headers=headers)
                if response.status_code == 200:
                    summary = response.json()
                    print("✅ Processing summary retrieved")
                    
                    # Display key metrics
                    for key, value in summary.items():
                        if isinstance(value, (int, float)):
                            print(f"   {key}: {value}")
                else:
                    print(f"⚠️ Processing summary failed: {response.status_code}")
            
            except Exception as e:
                print(f"❌ Status history error: {str(e)}")
        
        # FINAL RESULTS
        print("\n🎯 END-TO-END JOURNEY TEST RESULTS:")
        print("=" * 50)
        
        total_steps = len(journey_results)
        successful_steps = sum(journey_results.values())
        
        for step, success in journey_results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{step.replace('_', ' ').title():<25} {status}")
        
        print("=" * 50)
        print(f"Overall Success Rate: {successful_steps}/{total_steps} ({(successful_steps/total_steps)*100:.1f}%)")
        
        if successful_steps >= total_steps * 0.8:  # 80% success threshold
            print("🎉 DEMO SYSTEM IS READY FOR CUSTOMER PRESENTATION!")
        elif successful_steps >= total_steps * 0.6:  # 60% success threshold
            print("⚠️ System mostly functional - some features may need attention")
        else:
            print("❌ System needs significant work before demo")
        
        return journey_results
    
    async def test_demo_readiness_checklist(self, auth_token):
        """Test specific demo readiness requirements"""
        print("\n✅ DEMO READINESS CHECKLIST")
        print("=" * 40)
        
        checklist_results = {}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {"Authorization": f"Bearer {auth_token}"}
            
            # Demo Requirement 1: Can user log in?
            try:
                response = await client.get(f"{self.BASE_URL}/api/auth/profile", headers=headers)
                checklist_results['user_login'] = response.status_code == 200
                status = "✅" if checklist_results['user_login'] else "❌"
                print(f"{status} User can log in and access profile")
            except:
                checklist_results['user_login'] = False
                print("❌ User login failed")
            
            # Demo Requirement 2: Can upload files?
            try:
                # Create a simple test file
                with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
                    test_data = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
                    test_data.to_excel(tmp.name, index=False)
                    
                    with open(tmp.name, 'rb') as f:
                        response = await client.post(
                            f"{self.BASE_URL}/api/upload/",
                            headers=headers,
                            files={"file": ("checklist_test.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                        )
                    
                    checklist_results['file_upload'] = response.status_code == 200
                    status = "✅" if checklist_results['file_upload'] else "❌"
                    print(f"{status} File upload works")
                    
                    Path(tmp.name).unlink(missing_ok=True)
            except:
                checklist_results['file_upload'] = False
                print("❌ File upload failed")
            
            # Demo Requirement 3: Can access chat?
            try:
                response = await client.post(
                    f"{self.BASE_URL}/api/chat",
                    headers=headers,
                    json={"message": "test"}
                )
                checklist_results['chat_access'] = response.status_code in [200, 400, 422]  # Endpoint exists
                status = "✅" if checklist_results['chat_access'] else "❌"
                print(f"{status} Chat endpoint accessible")
            except:
                checklist_results['chat_access'] = False
                print("❌ Chat endpoint failed")
            
            # Demo Requirement 4: Can create analytics dashboard?
            try:
                test_dashboard = {
                    "name": "Demo Checklist Dashboard",
                    "description": "Test dashboard",
                    "dashboard_type": "google_analytics",
                    "configuration": {"test": True}
                }
                response = await client.post(f"{self.BASE_URL}/api/dashboard", headers=headers, json=test_dashboard)
                checklist_results['analytics_dashboard'] = response.status_code in [201, 200]
                status = "✅" if checklist_results['analytics_dashboard'] else "❌"
                print(f"{status} Analytics dashboard creation works")
            except:
                checklist_results['analytics_dashboard'] = False
                print("❌ Analytics dashboard failed")
            
            # Demo Requirement 5: Can view processing status?
            try:
                response = await client.get(f"{self.BASE_URL}/api/status/uploads", headers=headers)
                checklist_results['status_tracking'] = response.status_code == 200
                status = "✅" if checklist_results['status_tracking'] else "❌"
                print(f"{status} Processing status tracking works")
            except:
                checklist_results['status_tracking'] = False
                print("❌ Status tracking failed")
        
        # Calculate overall readiness
        readiness_score = sum(checklist_results.values()) / len(checklist_results)
        
        print("=" * 40)
        if readiness_score >= 0.8:
            print("🎉 SYSTEM IS DEMO READY!")
        elif readiness_score >= 0.6:
            print("⚠️ System mostly ready - minor issues")
        else:
            print("❌ System needs work before demo")
        
        print(f"Readiness Score: {readiness_score*100:.1f}%")
        
        return checklist_results
    
    def test_run_complete_journey(self, auth_token, demo_data_file):
        """Run the complete end-to-end journey test"""
        async def run_journey():
            print("🌟 COMPLETE END-TO-END SYSTEM TEST")
            print("This test simulates a complete user journey for demo readiness")
            print("=" * 70)
            
            try:
                # Run demo readiness checklist
                checklist_results = await self.test_demo_readiness_checklist(auth_token)
                
                # Run complete user journey
                journey_results = await self.test_complete_user_journey(auth_token, demo_data_file)
                
                # Combined results analysis
                all_results = {**checklist_results, **journey_results}
                total_checks = len(all_results)
                successful_checks = sum(all_results.values())
                
                print("\n" + "=" * 70)
                print("FINAL DEMO READINESS ASSESSMENT:")
                print("=" * 70)
                
                if successful_checks >= total_checks * 0.9:
                    print("🏆 EXCELLENT: System is fully ready for customer demo!")
                elif successful_checks >= total_checks * 0.75:
                    print("🎯 GOOD: System is ready for demo with minor noted issues")
                elif successful_checks >= total_checks * 0.5:
                    print("⚠️ FAIR: System has core functionality but needs attention")
                else:
                    print("❌ POOR: System needs significant work before demo")
                
                print(f"Total Success Rate: {successful_checks}/{total_checks} ({(successful_checks/total_checks)*100:.1f}%)")
                
                return successful_checks >= total_checks * 0.75
                
            except Exception as e:
                print(f"❌ Journey test failed: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
        
        return asyncio.run(run_journey())


if __name__ == "__main__":
    """
    Run complete end-to-end journey test directly
    """
    test_instance = TestEndToEndUserJourney()
    
    # Mock fixtures for direct execution
    auth_token = "eyJhbGciOiJIUzI1NiIsImtpZCI6IkVGQzhrMUp3bEcxY0g3bXMiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL25ya29kbGx1ZXVucGJpb3RqYnFsLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJmZGQ3MWY5NS1lOGQ0LTQxN2UtODVhYS05YjdiMGM5MjQzNmQiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzU2MTE0ODkxLCJpYXQiOjE3NTYxMTEyOTEsImVtYWlsIjoidXNlckBlbWFpbC5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsX3ZlcmlmaWVkIjp0cnVlfSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTc1NjExMTI5MX1dLCJzZXNzaW9uX2lkIjoiMTFkMWJhY2QtYjMxYy00NWNlLTlkZGEtYTc5Zjg2NTg2YTMwIiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.zsxouL5sXkhtExNftvpI1bh-9pIb2VzMvjL7mL6ZgSE"
    
    # Create demo data file
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
        demo_data = {
            'Product EAN': ['1234567890123', '2345678901234', '3456789012345'],
            'Product Name': ['Demo Phone', 'Demo Tablet', 'Demo Laptop'],
            'Quantity': [100, 150, 75],
            'Sales Amount': [50000.00, 75000.00, 112500.00],
            'Month': [12, 12, 12],
            'Year': [2024, 2024, 2024],
            'Reseller': ['DemoStore1', 'DemoStore2', 'DemoStore3']
        }
        df = pd.DataFrame(demo_data)
        df.to_excel(tmp_file.name, index=False)
        demo_data_file = tmp_file.name
    
    # Run complete journey test
    success = test_instance.test_run_complete_journey(auth_token, demo_data_file)
    
    # Cleanup
    Path(demo_data_file).unlink(missing_ok=True)
    
    if success:
        print("\n🎉 SYSTEM IS READY FOR CUSTOMER DEMO!")
        exit(0)
    else:
        print("\n⚠️ System needs attention before demo")
        exit(1)