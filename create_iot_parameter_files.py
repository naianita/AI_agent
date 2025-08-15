#!/usr/bin/env python3
"""
Create individual IoT parameter CSV files for file search functionality
"""
import sqlite3
import csv
import os
import sys

def create_parameter_files():
    """Create individual CSV files for each IoT parameter"""
    
    # Use the same database path as the main export script
    db_path = '../SML_STEM_IoT.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Define the parameters we want to extract
        target_parameters = ['CO2', 'Humidity', 'Temperature', 'TVOC']
        
        print("Creating IoT parameter files for file search...")
        
        for param in target_parameters:
            output_file = f'../iot_{param.lower()}_data.csv'
            print(f"Creating {output_file}...")
            
            # Query data for this parameter
            cursor.execute("""
                SELECT 
                    id,
                    sensor,
                    parameter,
                    datetime(timestamp/1000, 'unixepoch') as readable_time,
                    timestamp,
                    value
                FROM data 
                WHERE parameter = ?
                ORDER BY timestamp DESC
                LIMIT 5000;
            """, (param,))
            
            rows = cursor.fetchall()
            
            if not rows:
                print(f"⚠️  No data found for parameter: {param}")
                continue
            
            # Write to CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['ID', 'Sensor', 'Parameter', 'DateTime', 'Timestamp', 'Value'])
                writer.writerows(rows)
            
            # Get file info
            size_kb = os.path.getsize(output_file) / 1024
            print(f"✓ Created {output_file} with {len(rows)} records ({size_kb:.1f} KB)")
        
        conn.close()
        print("\n✅ All parameter files created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating parameter files: {e}")
        return False

if __name__ == "__main__":
    success = create_parameter_files()
    sys.exit(0 if success else 1)