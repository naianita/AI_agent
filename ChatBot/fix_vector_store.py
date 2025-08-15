#!/usr/bin/env python3
"""
Advanced troubleshooting and fixing for vector store file attachment issues
"""
import os
import sys
import django
import json
import time
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatBot.settings')
django.setup()

from django.conf import settings
from openai import OpenAI

def diagnose_and_fix():
    """Comprehensive diagnosis and fix for vector store issues"""
    
    print("🔧 VECTOR STORE DIAGNOSTIC & REPAIR TOOL")
    print("=" * 60)
    
    # Initialize client
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Load configuration
    try:
        with open('file_search_config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ No configuration file found. Run upload_iot_files.py first.")
        return False
    
    vector_store_id = config['vector_store_id']
    file_ids = config['file_ids']
    
    print(f"📍 Vector Store: {vector_store_id}")
    print(f"📁 Files to check: {len(file_ids)}")
    
    # Step 1: Check vector store status
    print(f"\n🔍 STEP 1: Checking vector store health...")
    try:
        vector_store = client.vector_stores.retrieve(vector_store_id)
        print(f"   ✅ Vector store exists: {vector_store.name}")
        print(f"   📊 Status: {vector_store.status}")
        print(f"   📁 File counts: {vector_store.file_counts}")
        
    except Exception as e:
        print(f"   ❌ Vector store issue: {e}")
        return recreate_vector_store(client, file_ids)
    
    # Step 2: Check individual files
    print(f"\n🔍 STEP 2: Checking file status...")
    valid_files = []
    
    for file_id in file_ids:
        try:
            file_obj = client.files.retrieve(file_id)
            print(f"   ✅ {file_id}: {file_obj.filename} ({file_obj.bytes} bytes, {file_obj.status})")
            valid_files.append(file_id)
            
        except Exception as e:
            print(f"   ❌ {file_id}: {e}")
            continue
    
    if len(valid_files) != len(file_ids):
        print(f"   ⚠️  Only {len(valid_files)}/{len(file_ids)} files are valid")
    
    # Step 3: Try different attachment strategies
    print(f"\n🔧 STEP 3: Trying different attachment strategies...")
    
    # Strategy 1: Single file with retry
    success_count = try_single_file_attachment(client, vector_store_id, valid_files)
    
    if success_count == len(valid_files):
        print(f"\n🎉 SUCCESS: All {success_count} files attached!")
        update_config(config, valid_files)
        return True
    
    # Strategy 2: Recreate vector store if partial failure
    if success_count < len(valid_files):
        print(f"\n🔄 STRATEGY 2: Recreating vector store...")
        return recreate_vector_store(client, valid_files)
    
    return False

def try_single_file_attachment(client, vector_store_id, file_ids):
    """Try attaching files one by one with retries and delays"""
    
    # Check current attachments
    try:
        current_files = client.vector_stores.files.list(vector_store_id=vector_store_id)
        attached_ids = [f.id for f in current_files.data]
        print(f"   📋 Currently attached: {len(attached_ids)} files")
    except:
        attached_ids = []
    
    success_count = len(attached_ids)
    
    for i, file_id in enumerate(file_ids):
        if file_id in attached_ids:
            print(f"   ✅ {file_id} already attached")
            continue
        
        print(f"   🔄 Attaching {file_id} ({i+1}/{len(file_ids)})...")
        
        # Try with multiple retry attempts
        for attempt in range(3):
            try:
                if attempt > 0:
                    delay = 2 ** attempt  # Exponential backoff: 2s, 4s, 8s
                    print(f"      ⏳ Retry {attempt+1}/3 after {delay}s delay...")
                    time.sleep(delay)
                
                result = client.vector_stores.files.create(
                    vector_store_id=vector_store_id,
                    file_id=file_id
                )
                
                print(f"   ✅ Successfully attached {file_id}")
                success_count += 1
                break
                
            except Exception as e:
                error_msg = str(e)
                if "500" in error_msg:
                    print(f"      ❌ Server error (attempt {attempt+1}/3): {e}")
                elif "400" in error_msg:
                    print(f"      ❌ Client error: {e}")
                    break  # Don't retry 400 errors
                else:
                    print(f"      ❌ Unexpected error: {e}")
        
        # Small delay between files
        if i < len(file_ids) - 1:
            time.sleep(1)
    
    return success_count

def recreate_vector_store(client, file_ids):
    """Create a new vector store and attach files"""
    
    print(f"🆕 Creating new vector store...")
    
    try:
        # Create new vector store
        new_vector_store = client.vector_stores.create(
            name=f"iot_knowledge_base_fixed_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            metadata={
                "description": "Fixed IoT sensor data vector store",
                "created_for": "expert_evaluation_fixed",
                "created_at": datetime.now().isoformat()
            }
        )
        
        print(f"   ✅ New vector store created: {new_vector_store.id}")
        
        # Try batch attachment first
        print(f"   🔄 Trying batch attachment...")
        try:
            batch_result = client.vector_stores.file_batches.create(
                vector_store_id=new_vector_store.id,
                file_ids=file_ids
            )
            
            # Wait for batch to complete
            print(f"   ⏳ Waiting for batch processing...")
            for i in range(30):  # Wait up to 5 minutes
                batch_status = client.vector_stores.file_batches.retrieve(
                    vector_store_id=new_vector_store.id,
                    batch_id=batch_result.id
                )
                
                if batch_status.status == "completed":
                    print(f"   ✅ Batch attachment successful!")
                    update_config_with_new_store(new_vector_store.id, file_ids)
                    return True
                elif batch_status.status == "failed":
                    print(f"   ❌ Batch attachment failed")
                    break
                
                time.sleep(10)  # Check every 10 seconds
                
        except Exception as e:
            print(f"   ⚠️  Batch attachment failed: {e}")
        
        # Fallback to individual attachment
        print(f"   🔄 Fallback: Individual file attachment...")
        success_count = try_single_file_attachment(client, new_vector_store.id, file_ids)
        
        if success_count == len(file_ids):
            print(f"   ✅ All files attached to new vector store!")
            update_config_with_new_store(new_vector_store.id, file_ids)
            return True
        else:
            print(f"   ⚠️  Only {success_count}/{len(file_ids)} files attached")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to create new vector store: {e}")
        return False

def update_config(config, successful_file_ids):
    """Update configuration with successful attachments"""
    config['attached_files'] = successful_file_ids
    config['last_fix_attempt'] = datetime.now().isoformat()
    
    with open('file_search_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"💾 Configuration updated")

def update_config_with_new_store(new_vector_store_id, file_ids):
    """Update configuration with new vector store"""
    config = {
        "vector_store_id": new_vector_store_id,
        "file_ids": file_ids,
        "attached_files": file_ids,
        "created_at": datetime.now().isoformat(),
        "status": "fixed_and_working",
        "file_names": [
            "iot_co2_data.csv",
            "iot_humidity_data.csv",
            "iot_temperature_data.csv",
            "iot_tvoc_data.csv"
        ]
    }
    
    with open('file_search_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"💾 Configuration updated with new vector store: {new_vector_store_id}")

if __name__ == "__main__":
    print("🚀 Starting vector store repair...")
    success = diagnose_and_fix()
    
    if success:
        print(f"\n✅ REPAIR SUCCESSFUL!")
        print(f"🧪 Ready to test: python expert_evaluation_runner.py")
    else:
        print(f"\n❌ REPAIR FAILED")
        print(f"🔍 Check OpenAI status or file formats")
        sys.exit(1)