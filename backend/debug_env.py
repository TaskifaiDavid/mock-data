#\!/usr/bin/env python3
import os
from app.utils.config import get_settings

try:
    settings = get_settings()
    print(f"Supabase URL: {settings.supabase_url}")
    print(f"Environment: {getattr(settings, 'environment', 'Not set')}")
    print(f"Debug Logging: {getattr(settings, 'debug_logging', 'Not set')}")
    print(f"JWT Secret (first 10 chars): {settings.jwt_secret_key[:10]}...")
except Exception as e:
    print(f"Error loading settings: {e}")
