#!/usr/bin/env python3
"""
Upload IoT CSV files to OpenAI and create vector store
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

def upload_and_setup():
    """Upload IoT CSV files and create vector store"""
    
    print("🚀 Starting IoT file search setup...")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Define the IoT data files
    iot_files = [
        "../iot_co2_data.csv",
        "../iot_humidity_data.csv", 
        "../iot_temperature_data.csv",
        "../iot_tvoc_data.csv"
    ]
    
    # Step 1: Upload files to OpenAI File API
    print("\n📤 Step 1: Uploading files to OpenAI...")
    file_ids = []
    
    for file_path in iot_files:
        print(f"   Uploading {os.path.basename(file_path)}...")
        try:
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
    
    print(f"\n📊 Upload Summary: {len(file_ids)}/{len(iot_files)} files uploaded")
    
    # Step 2: Create vector store
    print("\n🗃️  Step 2: Creating vector store...")
    try:
        vector_store = client.vector_stores.create(
            name="iot_knowledge_base",
            metadata={
                "description": "Historical IoT sensor data (CO2, Humidity, Temperature, TVOC)",
                "created_for": "expert_evaluation",
                "created_at": datetime.now().isoformat()
            }
        )
        print(f"   ✅ Vector store created: {vector_store.id}")
        
    except Exception as e:
        print(f"   ❌ Failed to create vector store: {e}")
        return None
    
    # Step 3: Attach files to vector store
    print("\n🔗 Step 3: Attaching files to vector store...")
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
    
    # Step 4: Save configuration
    print("\n💾 Step 4: Saving configuration...")
    config = {
        "vector_store_id": vector_store.id,
        "file_ids": file_ids,
        "attached_files": attached_files,
        "created_at": datetime.now().isoformat(),
        "file_names": [os.path.basename(f) for f in iot_files]
    }
    
    with open("file_search_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"   ✅ Configuration saved to file_search_config.json")
    
    # Step 5: Status check
    print("\n📋 Step 5: Checking vector store status...")
    try:
        files_in_store = client.vector_stores.files.list(
            vector_store_id=vector_store.id
        )
        
        print(f"   📁 Files in vector store: {len(files_in_store.data)}")
        for file_obj in files_in_store.data:
            print(f"      - {file_obj.id}: {file_obj.status}")
            
    except Exception as e:
        print(f"   ⚠️  Could not check status: {e}")
    
    print(f"\n🎉 Setup Complete!")
    print(f"📍 Vector Store ID: {vector_store.id}")
    print(f"📁 Files attached: {len(attached_files)}")
    print(f"🔧 Ready for integration with expert_evaluation_runner.py")
    
    return vector_store.id

if __name__ == "__main__":
    vector_store_id = upload_and_setup()
    if vector_store_id:
        print(f"\n✅ Success! Vector Store: {vector_store_id}")
    else:
        print(f"\n❌ Setup failed")
        sys.exit(1)