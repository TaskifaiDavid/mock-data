#\!/usr/bin/env python3
import sys
import socket
from urllib.parse import urlparse
import requests

def test_supabase_url(url):
    """Test if a Supabase URL is valid and reachable"""
    print(f"Testing URL: {url}")
    
    # Basic format validation
    if not url.startswith('https://'):
        return False, "URL must start with https://"
    if not '.supabase.co' in url:
        return False, "URL must contain .supabase.co domain"
    if 'your-project-id' in url:
        return False, "URL still contains placeholder text"
    
    # DNS resolution test
    try:
        parsed = urlparse(url)
        ip = socket.gethostbyname(parsed.hostname)
        print(f"✅ DNS resolves to: {ip}")
    except socket.gaierror as e:
        return False, f"DNS resolution failed: {e}"
    
    # HTTP connectivity test
    try:
        response = requests.get(f"{url}/rest/v1/", timeout=10)
        if response.status_code == 401:  # Expected for unauthenticated request
            print("✅ Supabase API is reachable (401 is expected)")
            return True, "URL is valid and Supabase API is reachable"
        else:
            print(f"⚠️  Got HTTP {response.status_code} (might still be valid)")
            return True, f"URL is reachable, returned HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"HTTP connection failed: {e}"

if __name__ == "__main__":
    if len(sys.argv) \!= 2:
        print("Usage: python test_supabase_url.py <supabase-url>")
        print("Example: python test_supabase_url.py https://abcdefg.supabase.co")
        sys.exit(1)
    
    url = sys.argv[1]
    valid, message = test_supabase_url(url)
    print(f"Result: {'✅ VALID' if valid else '❌ INVALID'} - {message}")
