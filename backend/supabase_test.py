#!/usr/bin/env python3
"""
Comprehensive Supabase connection test and configuration helper
"""
import os
import sys
import socket
from urllib.parse import urlparse

def test_dns_resolution(url):
    """Test if hostname resolves"""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        ip = socket.gethostbyname(hostname)
        return True, ip
    except socket.gaierror as e:
        return False, str(e)

def test_url_format(url):
    """Validate Supabase URL format"""
    if not url.startswith('https://'):
        return False, "URL must start with https://"
    if not '.supabase.co' in url:
        return False, "URL must contain .supabase.co"
    if 'your-project-id' in url:
        return False, "URL contains placeholder 'your-project-id'"
    return True, "URL format is valid"

def test_jwt_format(token):
    """Basic JWT format validation"""
    if not token.startswith('eyJ'):
        return False, "JWT should start with 'eyJ'"
    parts = token.split('.')
    if len(parts) != 3:
        return False, f"JWT should have 3 parts separated by dots, found {len(parts)}"
    return True, "JWT format appears valid"

def main():
    print("🔧 SUPABASE CONNECTION DIAGNOSTIC TOOL")
    print("=" * 50)
    
    # Test current environment
    try:
        from app.utils.config import get_settings
        settings = get_settings()
        url = settings.supabase_url
        anon_key = settings.supabase_anon_key
        service_key = settings.supabase_service_key
    except Exception as e:
        print(f"❌ Failed to load settings: {e}")
        return
    
    print(f"📍 Current Supabase URL: {url}")
    print(f"🔑 Anon Key (first 20 chars): {anon_key[:20]}...")
    print(f"🔐 Service Key (first 20 chars): {service_key[:20]}...")
    print()
    
    # Test URL format
    print("🧪 TESTING URL FORMAT:")
    url_valid, url_msg = test_url_format(url)
    print(f"   {'✅' if url_valid else '❌'} {url_msg}")
    
    # Test DNS resolution
    print("🌐 TESTING DNS RESOLUTION:")
    dns_valid, dns_result = test_dns_resolution(url)
    print(f"   {'✅' if dns_valid else '❌'} {'Resolves to: ' + dns_result if dns_valid else 'DNS Error: ' + dns_result}")
    
    # Test JWT format
    print("🔐 TESTING JWT FORMAT:")
    anon_valid, anon_msg = test_jwt_format(anon_key)
    print(f"   {'✅' if anon_valid else '❌'} Anon Key: {anon_msg}")
    
    service_valid, service_msg = test_jwt_format(service_key)
    print(f"   {'✅' if service_valid else '❌'} Service Key: {service_msg}")
    
    # Summary
    print("📊 DIAGNOSTIC SUMMARY:")
    all_valid = url_valid and dns_valid and anon_valid and service_valid
    print(f"   Overall Status: {'✅ READY' if all_valid else '❌ CONFIGURATION NEEDED'}")
    
    if not all_valid:
        print("🛠️  REQUIRED ACTIONS:")
        if not url_valid:
            print("   1. Update SUPABASE_URL with your real project URL")
        if not dns_valid:
            print("   2. Ensure the Supabase URL is valid and reachable")
        if not anon_valid:
            print("   3. Update SUPABASE_ANON_KEY with valid JWT")
        if not service_valid:
            print("   4. Update SUPABASE_SERVICE_KEY with valid JWT")

if __name__ == "__main__":
    main()
