#!/usr/bin/env python3
"""
Convert IoT CSV files to JSON format for OpenAI file search
CSV files are not supported for embeddings, but JSON files are
"""
import os
import csv
import json
from datetime import datetime

def convert_csv_to_json():
    """Convert all IoT CSV files to JSON format for file search"""
    
    print("🔄 CONVERTING CSV FILES TO JSON FOR FILE SEARCH")
    print("=" * 60)
    
    # Define the CSV files to convert
    csv_files = [
        "../iot_co2_data.csv",
        "../iot_humidity_data.csv", 
        "../iot_temperature_data.csv",
        "../iot_tvoc_data.csv"
    ]
    
    converted_files = []
    
    for csv_file in csv_files:
        if not os.path.exists(csv_file):
            print(f"❌ File not found: {csv_file}")
            continue
        
        # Create JSON filename
        base_name = os.path.basename(csv_file)
        json_file = base_name.replace('.csv', '.json')
        json_path = f"../{json_file}"
        
        print(f"\n📄 Converting {base_name} -> {json_file}")
        
        try:
            # Read CSV data
            records = []
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    records.append(row)
            
            print(f"   📊 Read {len(records)} records from CSV")
            
            # Create structured JSON for better searchability
            json_data = {
                "file_info": {
                    "filename": json_file,
                    "parameter": base_name.split('_')[1].upper(),  # CO2, HUMIDITY, etc.
                    "record_count": len(records),
                    "created_at": datetime.now().isoformat(),
                    "description": f"IoT sensor data for {base_name.split('_')[1]} measurements"
                },
                "environmental_standards": {
                    "CO2": {
                        "optimal": "< 400 ppm",
                        "acceptable": "< 1000 ppm", 
                        "poor": "> 1000 ppm"
                    },
                    "HUMIDITY": {
                        "optimal": "30-50%",
                        "acceptable": "40-60%"
                    },
                    "TEMPERATURE": {
                        "comfort": "20-24°C (68-75°F)"
                    },
                    "TVOC": {
                        "good": "< 220 ppb",
                        "moderate": "220-660 ppb",
                        "poor": "> 660 ppb"
                    }
                },
                "sensor_data": records,
                "data_summary": {
                    "total_readings": len(records),
                    "date_range": {
                        "earliest": records[0]["DateTime"] if records else None,
                        "latest": records[-1]["DateTime"] if records else None
                    }
                }
            }
            
            # Add searchable text content for better embeddings
            parameter = base_name.split('_')[1].upper()
            searchable_content = []
            
            # Add descriptive text
            searchable_content.append(f"This file contains {parameter} sensor measurements from IoT devices.")
            searchable_content.append(f"Total of {len(records)} {parameter} readings collected over time.")
            
            # Add sample data descriptions for better search
            if records:
                for i, record in enumerate(records[:10]):  # First 10 records
                    datetime_str = record.get('DateTime', 'unknown time')
                    value = record.get('Value', 'unknown value')
                    sensor = record.get('Sensor', 'unknown sensor')
                    
                    searchable_content.append(
                        f"{parameter} reading {i+1}: {value} {get_unit(parameter)} measured by {sensor} on {datetime_str}"
                    )
                
                # Add day-specific entries for better search (Wednesday, etc.)
                for record in records:
                    datetime_str = record.get('DateTime', '')
                    if 'Wed' in datetime_str or 'Wednesday' in datetime_str:
                        value = record.get('Value', 'unknown')
                        searchable_content.append(
                            f"Wednesday {parameter} measurement: {value} {get_unit(parameter)} on {datetime_str}"
                        )
            
            json_data["searchable_content"] = " ".join(searchable_content)
            
            # Write JSON file
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            file_size_kb = os.path.getsize(json_path) / 1024
            print(f"   ✅ Created {json_file} ({file_size_kb:.1f} KB)")
            
            converted_files.append(json_path)
            
        except Exception as e:
            print(f"   ❌ Failed to convert {csv_file}: {e}")
            continue
    
    print(f"\n📊 CONVERSION SUMMARY")
    print(f"✅ Converted {len(converted_files)}/{len(csv_files)} files to JSON")
    print(f"📁 JSON files created:")
    for json_file in converted_files:
        print(f"   • {os.path.basename(json_file)}")
    
    return converted_files

def get_unit(parameter):
    """Get the unit for each parameter type"""
    units = {
        "CO2": "ppm",
        "HUMIDITY": "%", 
        "TEMPERATURE": "°C",
        "TVOC": "ppb"
    }
    return units.get(parameter, "units")

def update_file_search_config(json_files):
    """Update the file search configuration to use JSON files"""
    
    print(f"\n🔧 Updating file search configuration...")
    
    try:
        # Load existing config
        with open('file_search_config.json', 'r') as f:
            config = json.load(f)
        
        # Update file names to JSON
        config['file_names'] = [os.path.basename(f) for f in json_files]
        config['format'] = 'json'
        config['updated_for_embeddings'] = datetime.now().isoformat()
        config['note'] = 'Updated to use JSON files - CSV not supported for embeddings'
        
        # Save updated config
        with open('file_search_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"   ✅ Updated file_search_config.json")
        
    except Exception as e:
        print(f"   ⚠️  Could not update config: {e}")

if __name__ == "__main__":
    print("🚀 Starting CSV to JSON conversion for file search...")
    
    json_files = convert_csv_to_json()
    
    if json_files:
        update_file_search_config(json_files)
        
        print(f"\n🎯 NEXT STEPS:")
        print(f"1. Upload JSON files: python upload_json_files.py")
        print(f"2. Test file search: python test_direct_vector_search.py")
        print(f"3. Run expert evaluation: python expert_evaluation_runner.py")
        
        print(f"\n✅ JSON files ready for OpenAI file search!")
    else:
        print(f"\n❌ No files converted successfully")
        exit(1)