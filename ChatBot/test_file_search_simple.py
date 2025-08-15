#!/usr/bin/env python3
"""
Simple test for file search setup with better debugging
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatBot.settings')
django.setup()

from django.conf import settings
from openai import OpenAI

def main():
    print("🔍 Testing file search setup...")
    
    # Test 1: Check API key
    print("\n1. Checking API key...")
    if hasattr(settings, 'OPENAI_API_KEY'):
        print(f"   ✅ API key found: {settings.OPENAI_API_KEY[:8]}...")
    else:
        print("   ❌ No API key in settings")
        return False
    
    # Test 2: Initialize OpenAI client
    print("\n2. Initializing OpenAI client...")
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        print("   ✅ OpenAI client initialized")
    except Exception as e:
        print(f"   ❌ Failed to initialize client: {e}")
        return False
    
    # Test 3: Check file existence
    print("\n3. Checking IoT files...")
    iot_files = [
        "../iot_co2_data.csv",
        "../iot_humidity_data.csv", 
        "../iot_temperature_data.csv",
        "../iot_tvoc_data.csv"
    ]
    
    for file_path in iot_files:
        if os.path.exists(file_path):
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"   ✅ {os.path.basename(file_path)} ({size_mb:.1f}MB)")
        else:
            print(f"   ❌ Missing: {file_path}")
    
    # Test 4: Try simple API call
    print("\n4. Testing OpenAI API connection...")
    try:
        # Simple test call
        response = client.models.list()
        print(f"   ✅ API connection working (found {len(response.data)} models)")
    except Exception as e:
        print(f"   ❌ API connection failed: {e}")
        return False
    
    print("\n🎉 All tests passed! Ready for file upload.")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup test failed")
        sys.exit(1)
    else:
        print("\n✅ Setup test successful")