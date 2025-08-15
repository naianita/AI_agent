#!/usr/bin/env python3
"""
Setup file search functionality for expert evaluation
Upload IoT data files to OpenAI and create vector store
"""
import os
import sys
import django
from openai import OpenAI

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatBot.settings')
django.setup()

from django.conf import settings

def setup_file_search():
    """Upload IoT CSV files to OpenAI and create vector store for file search"""
    
    # Initialize OpenAI client
    try:
        if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
            print("❌ OpenAI API key not found in settings")
            return None, None
        
        print(f"🔑 Using API key: {'*' * 20}{settings.OPENAI_API_KEY[-8:] if len(settings.OPENAI_API_KEY) > 8 else '***'}")
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
    except Exception as e:
        print(f"❌ Failed to initialize OpenAI client: {e}")
        return None, None
    
    # Define the IoT data files
    iot_files = [
        "../iot_co2_data.csv",
        "../iot_humidity_data.csv", 
        "../iot_temperature_data.csv",
        "../iot_tvoc_data.csv"
    ]
    
    print("🔄 Setting up file search for IoT data...")
    
    # Step 1: Upload files to OpenAI File API
    file_ids = []
    for file_path in iot_files:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            continue
            
        try:
            print(f"📤 Uploading {file_path}...")
            with open(file_path, "rb") as file_content:
                file_obj = client.files.create(
                    file=file_content,
                    purpose="assistants"
                )
            file_ids.append(file_obj.id)
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"✅ Uploaded {os.path.basename(file_path)} -> {file_obj.id} ({file_size_mb:.1f}MB)")
            
        except Exception as e:
            print(f"❌ Failed to upload {file_path}: {e}")
            continue
    
    if not file_ids:
        print("❌ No files were uploaded successfully")
        return None, None
    
    # Step 2: Create vector store
    try:
        print("🔄 Creating vector store...")
        vector_store = client.vector_stores.create(
            name="iot_knowledge_base",
            metadata={
                "description": "Historical IoT sensor data (CO2, Humidity, Temperature, TVOC)",
                "created_for": "expert_evaluation"
            }
        )
        print(f"✅ Created vector store: {vector_store.id}")
        
    except Exception as e:
        print(f"❌ Failed to create vector store: {e}")
        return None, None
    
    # Step 3: Add files to vector store
    attached_count = 0
    for file_id in file_ids:
        try:
            print(f"🔗 Attaching file {file_id} to vector store...")
            result = client.vector_stores.files.create(
                vector_store_id=vector_store.id,
                file_id=file_id
            )
            attached_count += 1
            print(f"✅ Attached file {file_id}")
            
        except Exception as e:
            print(f"❌ Failed to attach file {file_id}: {e}")
            continue
    
    # Step 4: Wait for processing and check status
    print("🔄 Checking vector store status...")
    try:
        files_in_store = client.vector_stores.files.list(
            vector_store_id=vector_store.id
        )
        ready_files = [f for f in files_in_store.data if f.status == "completed"]
        processing_files = [f for f in files_in_store.data if f.status == "in_progress"]
        
        print(f"📊 Vector store status:")
        print(f"   - Ready files: {len(ready_files)}")
        print(f"   - Processing files: {len(processing_files)}")
        print(f"   - Total attached: {len(files_in_store.data)}")
        
    except Exception as e:
        print(f"⚠️  Could not check vector store status: {e}")
    
    print(f"\n🎉 File search setup complete!")
    print(f"📍 Vector Store ID: {vector_store.id}")
    print(f"📁 Files attached: {attached_count}/{len(iot_files)}")
    
    return vector_store.id, file_ids

def save_config(vector_store_id, file_ids):
    """Save the vector store configuration for use in expert_evaluation_runner.py"""
    config = {
        "vector_store_id": vector_store_id,
        "file_ids": file_ids,
        "setup_timestamp": str(datetime.now())
    }
    
    import json
    with open("file_search_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"💾 Configuration saved to file_search_config.json")

if __name__ == "__main__":
    from datetime import datetime
    
    try:
        vector_store_id, file_ids = setup_file_search()
        
        if vector_store_id and file_ids:
            save_config(vector_store_id, file_ids)
            print(f"\n🚀 Ready to use file search in expert_evaluation_runner.py!")
            print(f"   Vector Store ID: {vector_store_id}")
        else:
            print("❌ Setup failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Unexpected error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)