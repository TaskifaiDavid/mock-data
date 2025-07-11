# HTTP Request Guide for Data Cleaning API

## Overview

This guide shows how to send HTTP requests to the data cleaning pipeline API. The system provides multiple integration methods, with the **Simple Webhook Endpoint** being the recommended approach for external integrations like Make.com.

**Base URL:** `http://localhost:8000` (adjust for your deployment)

---

## 🚀 Simple Webhook Endpoint (Recommended)

The easiest way to integrate with the API - **no authentication or email validation required!**

### Available Endpoints

#### Main Webhook
- **URL**: `http://localhost:8000/api/webhook` or `http://localhost:8000/api/webhook/`
- **Alternative**: `http://127.0.0.1:8000/api/webhook` (for tools that don't support localhost)
- **Method**: POST
- **Authentication**: None required
- **Content-Type**: application/json
- **Purpose**: Accept any JSON data for processing

#### Test Webhook
- **URL**: `http://localhost:8000/api/webhook/test`
- **Method**: POST
- **Authentication**: None required
- **Content-Type**: application/json
- **Purpose**: Testing with JSON validation

#### Health Check
- **URL**: `http://localhost:8000/api/webhook/health`
- **Method**: GET
- **Purpose**: Service health monitoring

### HTTP Client Configuration

#### For HTTP Client Tools (Postman, Insomnia, etc.)
```json
{
  "method": "POST",
  "url": "http://localhost:8000/api/webhook/",
  "headers": [
    {
      "name": "Content-Type",
      "value": "application/json"
    }
  ],
  "body": {
    "message": "Hello from Make.com",
    "data": {
      "any_field": "any_value",
      "email": "no_validation@needed.com",
      "custom_data": "flexible structure"
    }
  }
}
```

#### Response Format
```json
{
  "success": true,
  "message": "Webhook received successfully",
  "timestamp": "2025-07-11T21:40:50.172986",
  "received_data": {
    "message": "Hello from Make.com",
    "data": {
      "any_field": "any_value",
      "email": "no_validation@needed.com",
      "custom_data": "flexible structure"
    }
  }
}
```

### Python Example
```python
import requests
import json

# Simple webhook call
webhook_data = {
    "source": "make.com",
    "email": "user@anywhere.com",  # No email validation
    "message": "Processing request",
    "custom_fields": {
        "project": "data_cleaning",
        "priority": "high"
    }
}

response = requests.post(
    "http://localhost:8000/api/webhook/",
    headers={"Content-Type": "application/json"},
    json=webhook_data
)

result = response.json()
print(f"Success: {result['success']}")
print(f"Message: {result['message']}")
print(f"Timestamp: {result['timestamp']}")
```

### JavaScript/Fetch Example
```javascript
const webhookData = {
  source: "make.com",
  email: "user@anywhere.com",  // No email validation
  message: "Processing request",
  customFields: {
    project: "data_cleaning",
    priority: "high"
  }
};

fetch('http://localhost:8000/api/webhook/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(webhookData)
})
.then(response => response.json())
.then(data => {
  console.log('Success:', data.success);
  console.log('Message:', data.message);
  console.log('Timestamp:', data.timestamp);
})
.catch(error => console.error('Error:', error));
```

---

## 🔗 Make.com Integration

### Webhook Configuration for Make.com

#### HTTP Request Module Settings
```json
{
  "url": "http://127.0.0.1:8000/api/webhook",
  "method": "POST",
  "headers": [
    {
      "name": "Content-Type",
      "value": "application/json"
    }
  ],
  "bodyType": "raw",
  "contentType": "application/json",
  "data": "{\"source\": \"make.com\", \"email\": \"{{email}}\", \"message\": \"{{message}}\", \"timestamp\": \"{{now}}\"}"
}
```

#### Dynamic Data Example
```json
{
  "url": "http://127.0.0.1:8000/api/webhook",
  "method": "POST",
  "headers": [
    {
      "name": "Content-Type",
      "value": "application/json"
    }
  ],
  "data": "{\"email\": \"{{trigger.email}}\", \"file_url\": \"{{trigger.file_url}}\", \"processing_type\": \"{{1.processing_type}}\", \"metadata\": {\"source\": \"email\", \"received_at\": \"{{now}}\"}}"
}
```

#### Expected Response Handling
- **Success Response**: `200 OK` with `success: true`
- **Error Response**: `200 OK` with `success: false` and error message
- **Response Fields**: `success`, `message`, `timestamp`, `received_data`

### Make.com Scenario Examples

#### Email Attachment Processing
1. **Email Trigger**: Watch for emails with Excel attachments
2. **Download Attachment**: Save Excel file temporarily
3. **Webhook Call**: Send file metadata to webhook endpoint
4. **Process Response**: Handle success/failure appropriately

#### Scheduled Data Import
1. **Timer Trigger**: Run daily/weekly
2. **File Download**: Get files from cloud storage
3. **Webhook Call**: Notify API of new files available
4. **Status Check**: Monitor processing status

---

## 📁 File Upload Integration (Requires Authentication)

For direct file uploads, authentication is required. This section covers the traditional upload approach.

### Authentication Setup

#### Register New User
**HTTP Client Configuration:**
```json
{
  "method": "POST",
  "url": "http://localhost:8000/api/auth/register",
  "headers": [
    {
      "name": "Content-Type",
      "value": "application/json"
    }
  ],
  "body": {
    "email": "test@example.com",
    "password": "password123"
  }
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user-uuid",
    "email": "test@example.com"
  }
}
```

#### Login (Existing Users)
**HTTP Client Configuration:**
```json
{
  "method": "POST",
  "url": "http://localhost:8000/api/auth/login",
  "headers": [
    {
      "name": "Content-Type",
      "value": "application/json"
    }
  ],
  "body": {
    "email": "test@example.com",
    "password": "password123"
  }
}
```

### File Upload

#### Single File Upload
**HTTP Client Configuration:**
```json
{
  "method": "POST",
  "url": "http://localhost:8000/api/upload/",
  "headers": [
    {
      "name": "Authorization",
      "value": "Bearer YOUR_TOKEN_HERE"
    }
  ],
  "body": "multipart/form-data with file field"
}
```

**Python Example:**
```python
import requests

# Authentication
auth_response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={
        "email": "test@example.com",
        "password": "password123"
    }
)
token = auth_response.json()["access_token"]

# File upload
headers = {"Authorization": f"Bearer {token}"}
files = {"file": open("sales_data.xlsx", "rb")}

response = requests.post(
    "http://localhost:8000/api/upload/",
    headers=headers,
    files=files
)

upload_data = response.json()
upload_id = upload_data["id"]
print(f"Upload ID: {upload_id}")
print(f"Status: {upload_data['status']}")
```

#### Multiple File Upload
**HTTP Client Configuration:**
```json
{
  "method": "POST",
  "url": "http://localhost:8000/api/upload/multiple",
  "headers": [
    {
      "name": "Authorization",
      "value": "Bearer YOUR_TOKEN_HERE"
    }
  ],
  "body": "multipart/form-data with multiple files field"
}
```

**Python Example:**
```python
import requests

headers = {"Authorization": f"Bearer {token}"}
files = [
    ("files", open("skins_nl_data.xlsx", "rb")),
    ("files", open("boxnox_data.xlsx", "rb")), 
    ("files", open("aromateque_data.xlsx", "rb"))
]

response = requests.post(
    "http://localhost:8000/api/upload/multiple",
    headers=headers,
    files=files
)

uploads = response.json()
for upload in uploads:
    print(f"File: {upload['filename']}, ID: {upload['id']}, Status: {upload['status']}")
```

### Status Tracking

#### Check Upload Status
**HTTP Client Configuration:**
```json
{
  "method": "GET",
  "url": "http://localhost:8000/api/status/550e8400-e29b-41d4-a716-446655440000",
  "headers": [
    {
      "name": "Authorization",
      "value": "Bearer YOUR_TOKEN_HERE"
    }
  ]
}
```

#### Status Values
- `PENDING`: File uploaded, waiting to be processed
- `PROCESSING`: Currently being cleaned and normalized
- `COMPLETED`: Successfully processed and stored
- `FAILED`: Processing failed (check error_message)

#### Python Polling Example
```python
import time
import requests

def wait_for_completion(upload_id, token, timeout=300):
    """Poll upload status until completion or timeout"""
    headers = {"Authorization": f"Bearer {token}"}
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = requests.get(
            f"http://localhost:8000/api/status/{upload_id}",
            headers=headers
        )
        
        status_data = response.json()
        status = status_data["status"]
        
        print(f"Status: {status}")
        
        if status in ["COMPLETED", "FAILED"]:
            return status_data
            
        time.sleep(5)  # Wait 5 seconds before checking again
    
    raise TimeoutError("Processing timeout")

# Usage
result = wait_for_completion(upload_id, token)
if result["status"] == "COMPLETED":
    print(f"Processed {result['rows_processed']} rows")
    print(f"Cleaned {result['rows_cleaned']} rows") 
    print(f"Processing time: {result['processing_time_ms']}ms")
else:
    print(f"Failed: {result.get('error_message', 'Unknown error')}")
```

---

## 🔧 Error Handling

### Common Errors

#### Authentication Errors
```json
{
  "detail": "Could not validate credentials"
}
```

#### File Validation Errors
```json
{
  "error": "Only ['.xlsx'] files are allowed"
}
```

#### File Size Errors
```json
{
  "error": "File size exceeds 10.0MB limit"
}
```

#### Processing Errors
```json
{
  "id": "upload-id",
  "status": "FAILED",
  "error_message": "Unable to read Excel file: Invalid file format"
}
```

### Error Handling in Python
```python
try:
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()  # Raises exception for HTTP errors
    
    result = response.json()
    if "error" in result:
        print(f"API Error: {result['error']}")
    elif result.get("success") is False:
        print(f"Webhook Error: {result.get('message', 'Unknown error')}")
    else:
        print(f"Success: {result.get('message', 'Request completed')}")
        
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
except KeyError as e:
    print(f"Unexpected response format: {e}")
```

---

## 🛠️ Troubleshooting

### Webhook Issues

#### 1. Connection Refused
- **Problem**: Server not running or wrong port
- **Solution**: Verify server is running on localhost:8000
- **Check**: Try health endpoint: `GET http://localhost:8000/api/webhook/health`

#### 2. Invalid JSON Format
- **Problem**: Malformed JSON in request body
- **Solution**: Validate JSON syntax before sending
- **Tools**: Use JSON validators or format checkers

#### 3. Server Error (500)
- **Problem**: Internal server error
- **Solution**: Check server logs for detailed error information
- **Debug**: Use test endpoint first: `POST http://localhost:8000/api/webhook/test`

#### 4. "IP address not valid" Error (Make.com)
- **Problem**: Configuration conflict in HTTP request module
- **Root Cause**: Mixed content types (e.g., `bodyType: "multipart_form_data"` with `Content-Type: application/json`)
- **Solution**: Use consistent configuration

**❌ Incorrect Configuration:**
```json
{
  "bodyType": "multipart_form_data",
  "headers": [{"name": "Content-Type", "value": "application/json"}],
  "formDataFields": [{"key": "message", "value": "Hi there"}]
}
```

**✅ Correct JSON Configuration:**
```json
{
  "url": "http://localhost:8000/api/webhook/",
  "method": "POST",
  "bodyType": "raw",
  "contentType": "application/json",
  "data": "{\"message\": \"Hi there\"}"
}
```

**✅ Correct Form Data Configuration:**
```json
{
  "url": "http://localhost:8000/api/webhook/",
  "method": "POST",
  "bodyType": "multipart_form_data",
  "formDataFields": [
    {"key": "message", "value": "Hi there", "fieldType": "text"}
  ]
}
```

**Note**: This error occurs in Make.com's client-side validation, not from the server.

### Authentication Issues (File Upload Only)

#### 1. 401 Unauthorized
- **Problem**: Invalid or expired token
- **Solution**: Re-authenticate and get new token
- **Debug**: Use debug endpoint: `GET http://localhost:8000/api/auth/debug-token`

#### 2. Email Validation Errors
- **Problem**: Invalid email format during registration/login
- **Solution**: Use standard email formats (user@domain.com)
- **Recommendation**: Use webhook endpoint to avoid email validation

### File Upload Issues

#### 1. 413 Payload Too Large
- **Problem**: File exceeds 10MB limit
- **Solution**: Compress file or split into smaller files

#### 2. 422 Validation Error
- **Problem**: File format not supported
- **Solution**: Ensure file is .xlsx format

#### 3. Processing Stuck
- **Problem**: File processing not completing
- **Solution**: Check server logs, may need restart

### API Endpoint Issues

#### 1. 404 Not Found
**Common Mistakes:**
- ❌ `/api/login` → ✅ `/api/auth/login`
- ❌ `/api/register` → ✅ `/api/auth/register`
- ❌ `/upload` → ✅ `/api/upload/`
- ❌ `/status` → ✅ `/api/status/`
- ❌ `/webhook` → ✅ `/api/webhook/`

### JSON Formatting Tips
- Always use double quotes for JSON strings
- Ensure proper closing quotes on all fields
- Check for missing commas between fields
- Validate JSON syntax before sending requests
- Use proper escaping for special characters

### Debug Mode
Check token validity (for authenticated endpoints):
**HTTP Client Configuration:**
```json
{
  "method": "GET",
  "url": "http://localhost:8000/api/auth/debug-token",
  "headers": [
    {
      "name": "Authorization",
      "value": "Bearer YOUR_TOKEN_HERE"
    }
  ]
}
```

### Integration Testing

#### Test Webhook Connectivity
```python
import requests

def test_webhook_connectivity():
    """Test if webhook endpoint is accessible"""
    try:
        response = requests.get("http://localhost:8000/api/webhook/health")
        if response.status_code == 200:
            print("✅ Webhook service is healthy")
            return True
        else:
            print(f"❌ Webhook service returned {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to webhook service: {e}")
        return False

def test_webhook_data():
    """Test webhook with sample data"""
    test_data = {
        "test": True,
        "message": "connectivity test",
        "timestamp": "2025-07-11T21:00:00Z"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/webhook/test",
            json=test_data
        )
        result = response.json()
        
        if result.get("success"):
            print("✅ Webhook data processing works")
            return True
        else:
            print(f"❌ Webhook failed: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook test failed: {e}")
        return False

# Run tests
if test_webhook_connectivity() and test_webhook_data():
    print("🎉 Webhook integration ready!")
else:
    print("💥 Webhook integration needs attention")
```

---

## 📊 Advanced Features

### Vendor Detection
The system automatically detects these vendors based on filename and sheet structure:

- **Skins NL**: Looks for "SalesPerSKU" sheet
- **BOXNOX**: Looks for "SELL OUT BY EAN" sheet  
- **Aromateque**: Looks for "TDSheet" sheet
- **Galilu**: Looks for "product_ranking_2025" sheet

### Data Transformations
Each vendor has specific cleaning rules:
- Date normalization
- EAN/barcode validation
- Quantity cleaning and validation
- Product name standardization
- Missing data handling

### Complete Integration Example

#### Full Python Script with Webhook
```python
#!/usr/bin/env python3
"""
Complete webhook integration example
"""
import requests
import json
import sys
from datetime import datetime

class WebhookClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def test_connectivity(self):
        """Test webhook service connectivity"""
        try:
            response = requests.get(f"{self.base_url}/api/webhook/health")
            response.raise_for_status()
            print("✅ Webhook service is healthy")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to webhook service: {e}")
            return False
    
    def send_webhook(self, data):
        """Send data to webhook endpoint"""
        try:
            response = requests.post(
                f"{self.base_url}/api/webhook/",
                headers={"Content-Type": "application/json"},
                json=data
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("success"):
                print(f"✅ Webhook successful: {result['message']}")
                print(f"📋 Timestamp: {result['timestamp']}")
                return result
            else:
                print(f"❌ Webhook failed: {result.get('message')}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {e}")
            return None
    
    def send_test_webhook(self, data):
        """Send data to test webhook endpoint"""
        try:
            response = requests.post(
                f"{self.base_url}/api/webhook/test",
                headers={"Content-Type": "application/json"},
                json=data
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("success"):
                print(f"✅ Test webhook successful: {result['message']}")
                return result
            else:
                print(f"❌ Test webhook failed: {result.get('message')}")
                return None
                
        except Exception as e:
            print(f"❌ Test webhook error: {e}")
            return None

def main():
    # Example usage
    client = WebhookClient()
    
    # Test connectivity
    if not client.test_connectivity():
        print("💥 Cannot connect to webhook service")
        sys.exit(1)
    
    # Send sample data
    sample_data = {
        "source": "python_script",
        "email": "user@example.com",  # No validation required
        "message": "Processing Excel file",
        "metadata": {
            "filename": "sales_data.xlsx",
            "vendor": "unknown",
            "received_at": datetime.now().isoformat()
        },
        "custom_fields": {
            "priority": "high",
            "notify_on_complete": True
        }
    }
    
    # Send to main webhook
    result = client.send_webhook(sample_data)
    if result:
        print("🎉 Main webhook integration successful!")
    
    # Test with validation
    test_result = client.send_test_webhook(sample_data)
    if test_result:
        print("🎉 Test webhook integration successful!")

if __name__ == "__main__":
    main()
```

### Usage
```bash
python webhook_example.py
```

---

## 📞 Support

For additional support:
- Check server logs for detailed error information
- Use health check endpoints to verify service status
- Test with simple data before complex integrations
- Contact system administrator for server-related issues

### Quick Reference

#### Primary Integration (Recommended)
- **Webhook URL**: `http://localhost:8000/api/webhook/`
- **Method**: POST
- **Auth**: None required
- **Format**: JSON

#### Alternative Integration
- **Upload URL**: `http://localhost:8000/api/upload/`
- **Method**: POST
- **Auth**: Bearer token required
- **Format**: multipart/form-data

#### Health Checks
- **Webhook**: `http://localhost:8000/api/webhook/health`
- **API**: `http://localhost:8000/health`