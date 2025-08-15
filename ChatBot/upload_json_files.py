#!/usr/bin/env python3
"""
Upload converted JSON files to OpenAI for file search
JSON files are supported for embeddings, unlike CSV
"""
import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatBot.settings')
django.setup()

from django.conf import settings
from openai import OpenAI

def upload_json_files():
    """Upload JSON IoT files to OpenAI and create vector store"""
    
    print("📤 UPLOADING JSON FILES FOR FILE SEARCH")
    print("=" * 60)
    
    # Initialize OpenAI client
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Define the JSON files to upload
    json_files = [
        "../iot_co2_data.json",
        "../iot_humidity_data.json", 
        "../iot_temperature_data.json",
        "../iot_tvoc_data.json"
    ]
    
    # Step 1: Upload JSON files to OpenAI
    print("📤 Step 1: Uploading JSON files...")
    file_ids = []
    
    for file_path in json_files:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            continue
            
        try:
            print(f"   Uploading {os.path.basename(file_path)}...")
            with open(file_path, "rb") as file_content:
                file_obj = client.files.create(
                    file=file_content,
                    purpose="assistants"
                )
            file_ids.append(file_obj.id)
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"   ✅ {os.path.basename(file_path)} -> {file_obj.id} ({file_size_mb:.1f}MB)")
            
        except Exception as e:
            print(f"   ❌ Failed to upload {file_path}: {e}")
            continue
    
    if not file_ids:
        print("❌ No files uploaded successfully")
        return False
    
    print(f"\n📊 Upload Summary: {len(file_ids)}/{len(json_files)} JSON files uploaded")
    
    # Step 2: Create new vector store for JSON files
    print(f"\n🗃️  Step 2: Creating vector store for JSON files...")
    try:
        vector_store = client.vector_stores.create(
            name="iot_json_knowledge_base",
            metadata={
                "description": "IoT sensor data in JSON format for file search",
                "format": "json",
                "created_for": "expert_evaluation_embeddings",
                "created_at": datetime.now().isoformat()
            }
        )
        print(f"   ✅ Vector store created: {vector_store.id}")
        
    except Exception as e:
        print(f"   ❌ Failed to create vector store: {e}")
        return False
    
    # Step 3: Attach JSON files to vector store
    print(f"\n🔗 Step 3: Attaching JSON files to vector store...")
    attached_files = []
    
    for file_id in file_ids:
        try:
            result = client.vector_stores.files.create(
                vector_store_id=vector_store.id,
                file_id=file_id
            )
            attached_files.append(file_id)
            print(f"   ✅ Attached {file_id}")
            
        except Exception as e:
            print(f"   ❌ Failed to attach {file_id}: {e}")
            continue
    
    # Step 4: Save updated configuration
    print(f"\n💾 Step 4: Saving JSON configuration...")
    config = {
        "vector_store_id": vector_store.id,
        "file_ids": file_ids,
        "attached_files": attached_files,
        "format": "json",
        "created_at": datetime.now().isoformat(),
        "file_names": [os.path.basename(f) for f in json_files],
        "note": "Using JSON files for embeddings support"
    }
    
    with open("file_search_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"   ✅ Configuration saved to file_search_config.json")
    
    # Step 5: Wait and check status
    print(f"\n📋 Step 5: Checking attachment status...")
    import time
    time.sleep(5)  # Wait a bit for processing
    
    try:
        files_in_store = client.vector_stores.files.list(
            vector_store_id=vector_store.id
        )
        
        print(f"   📁 Files in vector store: {len(files_in_store.data)}")
        for file_obj in files_in_store.data:
            print(f"      - {file_obj.id}: {file_obj.status}")
            
    except Exception as e:
        print(f"   ⚠️  Could not check status: {e}")
    
    print(f"\n🎉 JSON File Setup Complete!")
    print(f"📍 Vector Store ID: {vector_store.id}")
    print(f"📁 Files attached: {len(attached_files)}")
    print(f"🔧 Ready for file search testing!")
    
    return True

def test_json_file_search():
    """Quick test of JSON file search"""
    
    print(f"\n🧪 Testing JSON file search...")
    
    try:
        with open('file_search_config.json', 'r') as f:
            config = json.load(f)
        vector_store_id = config['vector_store_id']
    except:
        print("❌ No configuration found")
        return
    
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Test search queries
    test_queries = [
        "CO2 levels on Wednesday",
        "humidity data",
        "temperature readings",
        "TVOC measurements"
    ]
    
    for query in test_queries:
        try:
            results = client.vector_stores.search(
                vector_store_id=vector_store_id,
                query=query,
                max_num_results=2
            )
            
            if hasattr(results, 'data') and results.data:
                print(f"   ✅ '{query}': Found {len(results.data)} results")
                top_result = results.data[0]
                filename = getattr(top_result, 'filename', 'unknown')
                score = getattr(top_result, 'score', 'unknown')
                print(f"      📄 Top: {filename} (score: {score})")
            else:
                print(f"   📭 '{query}': No results")
                
        except Exception as e:
            print(f"   ❌ '{query}': Search failed - {e}")

if __name__ == "__main__":
    success = upload_json_files()
    
    if success:
        test_json_file_search()
        print(f"\n🚀 Ready to test:")
        print(f"   • python test_direct_vector_search.py")
        print(f"   • python expert_evaluation_runner.py")
    else:
        print(f"\n❌ Upload failed")
        sys.exit(1)