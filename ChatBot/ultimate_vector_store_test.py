#!/usr/bin/env python3
"""
ULTIMATE vector store diagnostic using ALL FOUR API endpoints:
1. LIST - What files are in the vector store
2. RETRIEVE - Individual file status  
3. CREATE - Attach missing files
4. CONTENT - View parsed file content (confirms file search ready)
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

def ultimate_vector_store_diagnostic():
    """Complete diagnostic using all 4 vector store API endpoints"""
    
    print("🚀 ULTIMATE VECTOR STORE DIAGNOSTIC")
    print("=" * 70)
    
    # Load configuration
    try:
        with open('file_search_config.json', 'r') as f:
            config = json.load(f)
        vector_store_id = config['vector_store_id']
        expected_files = config['file_ids']
        file_names = config.get('file_names', ['iot_co2_data.csv', 'iot_humidity_data.csv', 'iot_temperature_data.csv', 'iot_tvoc_data.csv'])
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
    print(f"📋 File names: {', '.join(file_names)}")
    
    # Step 1: LIST - What's in the vector store?
    print(f"\n🔍 STEP 1: LIST - Current vector store contents")
    print("-" * 60)
    
    list_url = f"https://api.openai.com/v1/vector_stores/{vector_store_id}/files"
    current_files = []
    
    try:
        response = requests.get(list_url, headers=base_headers)
        print(f"📊 LIST Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            current_files = result.get('data', [])
            print(f"✅ SUCCESS: Found {len(current_files)} files")
            
            if current_files:
                print("📋 Files currently in vector store:")
                for i, file_obj in enumerate(current_files, 1):
                    status = file_obj.get('status', 'unknown')
                    created = file_obj.get('created_at', 'unknown')
                    icon = "✅" if status == 'completed' else "⏳" if status == 'in_progress' else "❌"
                    print(f"   {i}. {icon} {file_obj['id']} ({status})")
            else:
                print("📭 Vector store is EMPTY")
        
        elif response.status_code == 401:
            print(f"❌ PERMISSION ERROR: {response.json()}")
            return diagnose_permissions()
        else:
            print(f"❌ LIST FAILED ({response.status_code}): {response.text}")
    
    except Exception as e:
        print(f"❌ LIST REQUEST FAILED: {e}")
    
    # Step 2: RETRIEVE - Detailed status of each expected file
    print(f"\n🔍 STEP 2: RETRIEVE - Individual file status")
    print("-" * 60)
    
    file_status_map = {}
    existing_files = []
    
    for i, file_id in enumerate(expected_files, 1):
        retrieve_url = f"https://api.openai.com/v1/vector_stores/{vector_store_id}/files/{file_id}"
        
        try:
            response = requests.get(retrieve_url, headers=base_headers)
            file_name = file_names[i-1] if i-1 < len(file_names) else f"file_{i}"
            
            if response.status_code == 200:
                file_data = response.json()
                status = file_data.get('status', 'unknown')
                last_error = file_data.get('last_error')
                created_at = file_data.get('created_at', 'unknown')
                
                file_status_map[file_id] = {
                    'status': status,
                    'error': last_error,
                    'exists_in_store': True,
                    'created_at': created_at,
                    'name': file_name
                }
                
                icon = "✅" if status == 'completed' else "⏳" if status == 'in_progress' else "❌"
                print(f"   {icon} {file_name}: {status}")
                
                if status == 'completed':
                    existing_files.append(file_id)
                elif last_error:
                    print(f"      └─ Error: {last_error}")
                    
            elif response.status_code == 404:
                file_status_map[file_id] = {
                    'status': 'not_in_store',
                    'error': 'Not attached to vector store',
                    'exists_in_store': False,
                    'name': file_name
                }
                print(f"   📭 {file_name}: NOT in vector store")
                
            elif response.status_code == 401:
                print(f"   ❌ PERMISSION ERROR for {file_name}")
                break
                
            else:
                print(f"   ❌ {file_name}: Unexpected error ({response.status_code})")
        
        except Exception as e:
            print(f"   ❌ {file_name}: Request failed - {e}")
    
    # Step 3: CONTENT - View parsed content of working files
    print(f"\n🔍 STEP 3: CONTENT - Verify file parsing")
    print("-" * 60)
    
    content_working = []
    
    if existing_files:
        print(f"📄 Checking content of {len(existing_files)} completed files...")
        
        for i, file_id in enumerate(existing_files, 1):
            content_url = f"https://api.openai.com/v1/vector_stores/{vector_store_id}/files/{file_id}/content"
            file_name = file_status_map[file_id]['name']
            
            try:
                # Note: Content endpoint might not need OpenAI-Beta header
                content_headers = {
                    "Authorization": f"Bearer {api_key}",
                }
                
                response = requests.get(content_url, headers=content_headers)
                print(f"   📄 {file_name}: Status {response.status_code}")
                
                if response.status_code == 200:
                    content_data = response.json()
                    content_items = content_data.get('content', [])
                    filename = content_data.get('filename', 'unknown')
                    
                    print(f"      ✅ Content accessible: {filename}")
                    print(f"      📊 Content chunks: {len(content_items)}")
                    
                    # Show sample of content
                    if content_items:
                        first_chunk = content_items[0]
                        if isinstance(first_chunk, dict) and 'text' in first_chunk:
                            sample_text = first_chunk['text'][:100]
                            print(f"      📝 Sample: {sample_text}...")
                        else:
                            print(f"      📝 Content type: {type(first_chunk)}")
                    
                    content_working.append(file_id)
                    
                elif response.status_code == 401:
                    print(f"      ❌ Permission error accessing content")
                elif response.status_code == 404:
                    print(f"      ❌ Content not found (file may not be fully processed)")
                else:
                    print(f"      ❌ Content error ({response.status_code}): {response.text[:100]}")
            
            except Exception as e:
                print(f"      ❌ Content request failed: {e}")
    else:
        print("📭 No completed files to check content for")
    
    # Step 4: CREATE - Try to fix missing files
    print(f"\n🔍 STEP 4: CREATE - Attempt to fix missing files")
    print("-" * 60)
    
    missing_files = [f for f, data in file_status_map.items() if not data.get('exists_in_store', False)]
    
    if not missing_files:
        print("✅ All expected files are in the vector store!")
    else:
        print(f"🔧 Attempting to attach {len(missing_files)} missing files...")
        
        create_url = f"https://api.openai.com/v1/vector_stores/{vector_store_id}/files"
        newly_attached = []
        
        for file_id in missing_files:
            file_name = file_status_map[file_id]['name']
            data = {"file_id": file_id}
            
            try:
                response = requests.post(create_url, headers=base_headers, json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ {file_name}: Successfully attached ({result.get('status', 'unknown')})")
                    newly_attached.append(file_id)
                    
                elif response.status_code == 401:
                    error_data = response.json()
                    print(f"   ❌ {file_name}: PERMISSION ERROR")
                    print(f"      └─ {error_data}")
                    break
                    
                elif response.status_code == 400:
                    error_data = response.json()
                    print(f"   ❌ {file_name}: CLIENT ERROR - {error_data}")
                    
                elif response.status_code == 500:
                    print(f"   ❌ {file_name}: SERVER ERROR (OpenAI issue)")
                    
                else:
                    print(f"   ❌ {file_name}: Unexpected error ({response.status_code})")
            
            except Exception as e:
                print(f"   ❌ {file_name}: Request failed - {e}")
            
            time.sleep(1)  # Rate limiting
        
        if newly_attached:
            print(f"🎉 Successfully attached {len(newly_attached)} new files!")
    
    # FINAL SUMMARY
    print(f"\n🎯 ULTIMATE DIAGNOSTIC SUMMARY")
    print("=" * 70)
    
    total_expected = len(expected_files)
    files_in_store = len([f for f, data in file_status_map.items() if data.get('exists_in_store', False)])
    completed_files = len([f for f, data in file_status_map.items() if data.get('status') == 'completed'])
    content_accessible = len(content_working)
    
    print(f"📁 Expected files: {total_expected}")
    print(f"🗄️ Files in vector store: {files_in_store}")
    print(f"✅ Completed files: {completed_files}")
    print(f"📄 Content accessible: {content_accessible}")
    
    # File search readiness assessment
    print(f"\n🚀 FILE SEARCH READINESS:")
    if content_accessible == total_expected:
        print("🎉 FULLY OPERATIONAL - All files ready for search!")
        print("✅ Ready to test: python expert_evaluation_runner.py")
        readiness_score = 100
    elif content_accessible > 0:
        percentage = (content_accessible / total_expected) * 100
        print(f"⚠️ PARTIALLY OPERATIONAL - {content_accessible}/{total_expected} files ({percentage:.0f}%)")
        print("🧪 Test with partial data: python expert_evaluation_runner.py")
        readiness_score = percentage
    else:
        print("❌ NOT OPERATIONAL - No files accessible for search")
        print("🔧 Fix permissions: Add 'Files: Read' to API key")
        print("🔄 Then retry: python retry_file_attachment.py")
        readiness_score = 0
    
    print(f"\n📊 Readiness Score: {readiness_score:.0f}%")
    
    return readiness_score > 0

def diagnose_permissions():
    """Diagnose specific permission issues"""
    print(f"\n🔧 PERMISSION DIAGNOSIS")
    print("-" * 40)
    print("Required API permissions for file search:")
    print("  ❌ Files: Read - Can't read uploaded files")
    print("  ✅ Files: Write - Can upload files") 
    print("  ✅ Assistants: Write - Can create vector stores")
    print("  ✅ Responses API: Write - Can use file search")
    print("\nFix: Add 'Files: Read' permission to your API key")
    return False

if __name__ == "__main__":
    success = ultimate_vector_store_diagnostic()
    sys.exit(0 if success else 1)