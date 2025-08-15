#!/usr/bin/env python3
"""
Test DIRECT vector store search API to verify IoT data is searchable
This bypasses file search tool and tests the underlying search functionality
"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatBot.settings')
django.setup()

from django.conf import settings
from openai import OpenAI

def test_direct_vector_search():
    """Test direct vector store search API with IoT-related queries"""
    
    print("🔍 DIRECT VECTOR STORE SEARCH TEST")
    print("=" * 60)
    
    # Load configuration
    try:
        with open('file_search_config.json', 'r') as f:
            config = json.load(f)
        vector_store_id = config['vector_store_id']
    except FileNotFoundError:
        print("❌ No configuration file found")
        return False
    
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    print(f"📍 Vector Store: {vector_store_id}")
    
    # Test queries related to our IoT data
    test_queries = [
        "CO2 levels on Wednesday",
        "humidity data",
        "temperature readings",
        "TVOC measurements",
        "air quality 720 ppm",
        "sensor data from March",
        "environmental monitoring",
        "What were the CO2 levels?",
        "Show me humidity readings above 60%",
        "Any temperature data available?"
    ]
    
    print(f"🧪 Testing {len(test_queries)} search queries...")
    
    successful_searches = 0
    total_results = 0
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print("-" * 40)
        
        try:
            # Direct vector store search API call
            results = client.vector_stores.search(
                vector_store_id=vector_store_id,
                query=query,
                max_num_results=3  # Limit for testing
            )
            
            search_results = results.data if hasattr(results, 'data') else []
            result_count = len(search_results)
            total_results += result_count
            
            if result_count > 0:
                successful_searches += 1
                print(f"   ✅ Found {result_count} results!")
                
                # Show details of top result
                top_result = search_results[0]
                score = getattr(top_result, 'score', 'unknown')
                filename = getattr(top_result, 'filename', 'unknown')
                file_id = getattr(top_result, 'file_id', 'unknown')
                
                print(f"   📄 Top result: {filename} (score: {score})")
                print(f"   🆔 File ID: {file_id}")
                
                # Show content preview
                if hasattr(top_result, 'content') and top_result.content:
                    content_items = top_result.content
                    if content_items and len(content_items) > 0:
                        first_content = content_items[0]
                        if hasattr(first_content, 'text'):
                            preview = first_content.text[:100]
                            print(f"   📝 Content preview: {preview}...")
                        else:
                            print(f"   📝 Content type: {type(first_content)}")
                else:
                    print(f"   📝 No content preview available")
                
                # Show other results briefly
                if result_count > 1:
                    print(f"   📋 Other results:")
                    for j, result in enumerate(search_results[1:], 2):
                        filename = getattr(result, 'filename', 'unknown')
                        score = getattr(result, 'score', 'unknown')
                        print(f"      {j}. {filename} (score: {score})")
            else:
                print(f"   📭 No results found")
        
        except Exception as e:
            print(f"   ❌ Search failed: {e}")
            continue
    
    # Test with specific IoT parameters
    print(f"\n🔬 SPECIFIC IoT PARAMETER TESTS")
    print("=" * 60)
    
    iot_specific_queries = [
        "720 ppm CO2",
        "humidity above 65%", 
        "temperature sensor readings",
        "TVOC air quality",
        "environmental data Wednesday"
    ]
    
    for query in iot_specific_queries:
        print(f"\n🧪 IoT Query: '{query}'")
        
        try:
            results = client.vector_stores.search(
                vector_store_id=vector_store_id,
                query=query,
                max_num_results=2
            )
            
            search_results = results.data if hasattr(results, 'data') else []
            
            if search_results:
                result = search_results[0]
                filename = getattr(result, 'filename', 'unknown')
                score = getattr(result, 'score', 'unknown')
                print(f"   ✅ Match: {filename} (relevance: {score})")
                
                # Try to show actual IoT data
                if hasattr(result, 'content') and result.content:
                    for content_item in result.content[:2]:  # Show first 2 content items
                        if hasattr(content_item, 'text'):
                            text = content_item.text.strip()
                            # Look for CSV-like data
                            if ',' in text and any(param in text.lower() for param in ['co2', 'humidity', 'temperature', 'tvoc']):
                                print(f"   📊 IoT Data: {text[:150]}...")
                                break
            else:
                print(f"   📭 No matches")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    # SUMMARY
    print(f"\n📊 DIRECT SEARCH SUMMARY")
    print("=" * 60)
    
    success_rate = (successful_searches / len(test_queries)) * 100 if test_queries else 0
    avg_results = total_results / len(test_queries) if test_queries else 0
    
    print(f"🎯 Successful searches: {successful_searches}/{len(test_queries)} ({success_rate:.0f}%)")
    print(f"📋 Total results found: {total_results}")
    print(f"📊 Average results per query: {avg_results:.1f}")
    
    # Determine vector store status
    if successful_searches >= len(test_queries) * 0.8:  # 80% success rate
        print(f"\n🎉 VECTOR STORE FULLY OPERATIONAL!")
        print(f"✅ IoT data is searchable and ready for file search tool")
        print(f"🚀 File search should work once permissions are fixed")
        status = "fully_operational"
    elif successful_searches > 0:
        print(f"\n⚠️ VECTOR STORE PARTIALLY WORKING")
        print(f"✅ Some IoT data is searchable")
        print(f"🔧 May need to re-upload some files")
        status = "partially_working"
    else:
        print(f"\n❌ VECTOR STORE NOT WORKING")
        print(f"📭 No searchable data found")
        print(f"🔧 Need to fix file attachment issues")
        status = "not_working"
    
    # Next steps
    print(f"\n🎯 NEXT STEPS:")
    if status == "fully_operational":
        print("1. Fix API permissions: Add 'Files: Read' to your API key")
        print("2. Test file search tool: python expert_evaluation_runner.py")
        print("3. File search should work perfectly now!")
    elif status == "partially_working":
        print("1. Re-run file attachment: python retry_file_attachment.py")
        print("2. Test again: python test_direct_vector_search.py")
        print("3. Once all files working, test file search tool")
    else:
        print("1. Check file upload status: python comprehensive_vector_store_test.py")
        print("2. Re-upload files if needed: python upload_iot_files.py")
        print("3. Fix permissions and try again")
    
    return status != "not_working"

def test_semantic_similarity():
    """Test semantic search capabilities with different query styles"""
    
    print(f"\n🧠 SEMANTIC SIMILARITY TEST")
    print("=" * 40)
    
    try:
        with open('file_search_config.json', 'r') as f:
            config = json.load(f)
        vector_store_id = config['vector_store_id']
    except FileNotFoundError:
        return
    
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Test different ways of asking for the same information
    similar_queries = [
        "What were the CO2 levels?",
        "Show me carbon dioxide readings", 
        "Air quality measurements for CO2",
        "Carbon dioxide concentration data"
    ]
    
    print("Testing semantic similarity with related queries...")
    
    for query in similar_queries:
        try:
            results = client.vector_stores.search(
                vector_store_id=vector_store_id,
                query=query,
                max_num_results=1
            )
            
            if hasattr(results, 'data') and results.data:
                result = results.data[0]
                score = getattr(result, 'score', 0)
                filename = getattr(result, 'filename', 'unknown')
                print(f"   📊 '{query[:30]}...' → {filename} ({score:.2f})")
            else:
                print(f"   📭 '{query[:30]}...' → No results")
                
        except Exception as e:
            print(f"   ❌ '{query[:30]}...' → Error: {e}")

if __name__ == "__main__":
    success = test_direct_vector_search()
    test_semantic_similarity()
    
    if success:
        print(f"\n✅ Vector store search is working!")
        print(f"🔧 Fix API permissions to enable file search tool")
    else:
        print(f"\n❌ Vector store search failed")
        print(f"🔧 Need to fix file attachment issues first")
    
    sys.exit(0 if success else 1)