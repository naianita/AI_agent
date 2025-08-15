#!/usr/bin/env python3
"""
Comprehensive vector store API test using all three endpoints:
1. LIST files in vector store
2. RETRIEVE individual file status  
3. CREATE (attach) new files if needed
"""
import os
import sys
import django
import json
import requests
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatBot.settings')
django.setup()

from django.conf import settings
from openai import OpenAI

def comprehensive_vector_store_test():
    """Test all vector store file operations comprehensively"""
    
    print("🔬 COMPREHENSIVE VECTOR STORE API TEST")
    print("=" * 60)
    
    # Load configuration
    try:
        with open('file_search_config.json', 'r') as f:
            config = json.load(f)
        vector_store_id = config['vector_store_id']
        expected_files = config['file_ids']
    except FileNotFoundError:
        print("❌ No configuration file found")
        return False
    
    api_key = settings.OPENAI_API_KEY
    base_headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }
    
    print(f"📍 Vector Store: {vector_store_id}")
    print(f"📁 Expected files: {len(expected_files)}")
    
    # TEST 1: LIST - What's currently in the vector store?
    print(f"\n1️⃣ LIST: What files are in the vector store?")
    print("-" * 50)
    
    list_url = f"https://api.openai.com/v1/vector_stores/{vector_store_id}/files"
    
    try:
        response = requests.get(list_url, headers=base_headers)
        print(f"📊 LIST Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            current_files = result.get('data', [])
            print(f"✅ SUCCESS: Found {len(current_files)} files")
            
            if current_files:
                print("📋 Current files in vector store:")
                for i, file_obj in enumerate(current_files, 1):
                    print(f"   {i}. {file_obj['id']} (status: {file_obj.get('status', 'unknown')})")
            else:
                print("📭 Vector store is EMPTY")
            
        elif response.status_code == 401:
            print(f"❌ PERMISSION ERROR: {response.json()}")
            return False
        else:
            print(f"❌ LIST FAILED ({response.status_code}): {response.text}")
            current_files = []
    
    except Exception as e:
        print(f"❌ LIST REQUEST FAILED: {e}")
        current_files = []
    
    # TEST 2: RETRIEVE - Check status of each expected file individually
    print(f"\n2️⃣ RETRIEVE: Individual file status check")
    print("-" * 50)
    
    file_status_map = {}
    
    for i, file_id in enumerate(expected_files, 1):
        retrieve_url = f"https://api.openai.com/v1/vector_stores/{vector_store_id}/files/{file_id}"
        
        try:
            response = requests.get(retrieve_url, headers=base_headers)
            print(f"📄 File {i}/{len(expected_files)} ({file_id}): Status {response.status_code}")
            
            if response.status_code == 200:
                file_data = response.json()
                status = file_data.get('status', 'unknown')
                last_error = file_data.get('last_error')
                file_status_map[file_id] = {
                    'status': status,
                    'error': last_error,
                    'exists_in_store': True
                }
                print(f"   ✅ Found in vector store: {status}")
                if last_error:
                    print(f"   ⚠️ Last error: {last_error}")
                    
            elif response.status_code == 404:
                file_status_map[file_id] = {
                    'status': 'not_found',
                    'error': 'File not in vector store',
                    'exists_in_store': False
                }
                print(f"   ❌ NOT in vector store")
                
            elif response.status_code == 401:
                print(f"   ❌ PERMISSION ERROR: {response.json()}")
                break
                
            else:
                print(f"   ❌ UNEXPECTED ({response.status_code}): {response.text}")
        
        except Exception as e:
            print(f"   ❌ RETRIEVE FAILED: {e}")
    
    # TEST 3: CREATE - Try to attach missing files
    print(f"\n3️⃣ CREATE: Attempt to attach missing files")
    print("-" * 50)
    
    missing_files = [f for f, data in file_status_map.items() if not data.get('exists_in_store', False)]
    
    if not missing_files:
        print("✅ All files are already in the vector store!")
    else:
        print(f"🔧 Attempting to attach {len(missing_files)} missing files...")
        
        create_url = f"https://api.openai.com/v1/vector_stores/{vector_store_id}/files"
        
        for i, file_id in enumerate(missing_files, 1):
            data = {"file_id": file_id}
            
            try:
                response = requests.post(create_url, headers=base_headers, json=data)
                print(f"📤 File {i}/{len(missing_files)} ({file_id}): Status {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ ATTACHED: {result.get('status', 'unknown')}")
                    
                elif response.status_code == 401:
                    error_data = response.json()
                    print(f"   ❌ PERMISSION ERROR: {error_data}")
                    print(f"      → Missing permission for file attachment")
                    break
                    
                elif response.status_code == 400:
                    error_data = response.json()
                    print(f"   ❌ CLIENT ERROR: {error_data}")
                    
                elif response.status_code == 500:
                    error_data = response.json()
                    print(f"   ❌ SERVER ERROR: {error_data}")
                    print(f"      → OpenAI server issue, try again later")
                    
                else:
                    print(f"   ❌ UNEXPECTED ({response.status_code}): {response.text}")
            
            except Exception as e:
                print(f"   ❌ CREATE FAILED: {e}")
            
            # Small delay between attempts
            time.sleep(1)
    
    # SUMMARY
    print(f"\n📊 COMPREHENSIVE SUMMARY")
    print("=" * 60)
    
    total_files = len(expected_files)
    files_in_store = len([f for f, data in file_status_map.items() if data.get('exists_in_store', False)])
    completed_files = len([f for f, data in file_status_map.items() if data.get('status') == 'completed'])
    failed_files = len([f for f, data in file_status_map.items() if data.get('status') == 'failed'])
    
    print(f"📁 Total expected files: {total_files}")
    print(f"✅ Files in vector store: {files_in_store}")
    print(f"🎯 Completed files: {completed_files}")
    print(f"❌ Failed files: {failed_files}")
    print(f"📭 Missing files: {total_files - files_in_store}")
    
    # Detailed status breakdown
    if file_status_map:
        print(f"\n📋 Detailed file status:")
        for file_id, data in file_status_map.items():
            status_icon = "✅" if data['status'] == 'completed' else "❌" if data['status'] == 'failed' else "⏳" if data['status'] == 'in_progress' else "❓"
            print(f"   {status_icon} {file_id}: {data['status']}")
            if data.get('error'):
                print(f"      └─ Error: {data['error']}")
    
    # Recommendations
    print(f"\n🎯 RECOMMENDATIONS:")
    if completed_files == total_files:
        print("🎉 ALL FILES WORKING! File search should be fully functional.")
        print("✅ Ready to test: python expert_evaluation_runner.py")
    elif files_in_store > 0:
        print(f"⚠️ Partial success: {files_in_store}/{total_files} files in vector store")
        print("🔄 Some files may still be processing or failed")
        print("🧪 Test anyway: python expert_evaluation_runner.py")
    else:
        print("❌ No files in vector store - attachment completely failed")
        print("🔧 Fix API permissions: Add 'Files: Read' to your API key")
        print("🔄 Then retry: python retry_file_attachment.py")
    
    return completed_files > 0

if __name__ == "__main__":
    success = comprehensive_vector_store_test()
    sys.exit(0 if success else 1)