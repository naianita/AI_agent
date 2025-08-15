import sqlite3
import pandas as pd
import json
from datetime import datetime
import os

def export_to_csv(output_file='iot_data_complete.csv'):
    """Export all data to a single CSV file"""
    print(f"Exporting to CSV: {output_file}")
    
    conn = sqlite3.connect('SML_STEM_IoT.db')
    
    # Read all data
    query = """
    SELECT id, sensor, parameter, timestamp, value,
           datetime(timestamp/1000, 'unixepoch') as readable_time
    FROM data 
    ORDER BY timestamp DESC
    """
    
    # Use chunked reading for large datasets
    chunk_size = 50000
    chunks = []
    
    print("Reading data in chunks...")
    for chunk in pd.read_sql_query(query, conn, chunksize=chunk_size):
        chunks.append(chunk)
        print(f"Processed {len(chunks) * chunk_size} records...")
    
    # Combine all chunks
    df = pd.concat(chunks, ignore_index=True)
    
    # Export to CSV
    df.to_csv(output_file, index=False)
    conn.close()
    
    print(f"✅ Exported {len(df):,} records to {output_file}")
    return output_file

def export_by_sensor():
    """Export data separated by sensor"""
    print("Exporting data by sensor...")
    
    conn = sqlite3.connect('SML_STEM_IoT.db')
    
    # Get list of sensors
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT sensor FROM data ORDER BY sensor")
    sensors = [row[0] for row in cursor.fetchall()]
    
    exported_files = []
    
    for sensor in sensors:
        filename = f'sensor_{sensor}_data.csv'
        print(f"Exporting sensor {sensor} data...")
        
        query = """
        SELECT id, sensor, parameter, timestamp, value,
               datetime(timestamp/1000, 'unixepoch') as readable_time
        FROM data 
        WHERE sensor = ?
        ORDER BY timestamp DESC
        """
        
        df = pd.read_sql_query(query, conn, params=(sensor,))
        df.to_csv(filename, index=False)
        
        exported_files.append(filename)
        print(f"✅ Exported {len(df):,} records for sensor {sensor} to {filename}")
    
    conn.close()
    return exported_files

def export_by_parameter():
    """Export data separated by parameter type"""
    print("Exporting data by parameter...")
    
    conn = sqlite3.connect('SML_STEM_IoT.db')
    
    # Get list of parameters
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT parameter FROM data ORDER BY parameter")
    parameters = [row[0] for row in cursor.fetchall()]
    
    exported_files = []
    
    for param in parameters:
        filename = f'{param.lower()}_data.csv'
        print(f"Exporting {param} data...")
        
        query = """
        SELECT id, sensor, parameter, timestamp, value,
               datetime(timestamp/1000, 'unixepoch') as readable_time
        FROM data 
        WHERE parameter = ?
        ORDER BY timestamp DESC
        """
        
        df = pd.read_sql_query(query, conn, params=(param,))
        df.to_csv(filename, index=False)
        
        exported_files.append(filename)
        print(f"✅ Exported {len(df):,} records for {param} to {filename}")
    
    conn.close()
    return exported_files

def export_to_json(output_file='iot_data_complete.json', limit=10000):
    """Export data to JSON (limited records due to size)"""
    print(f"Exporting to JSON: {output_file} (limited to {limit:,} records)")
    
    conn = sqlite3.connect('SML_STEM_IoT.db')
    
    query = """
    SELECT id, sensor, parameter, timestamp, value,
           datetime(timestamp/1000, 'unixepoch') as readable_time
    FROM data 
    ORDER BY timestamp DESC
    LIMIT ?
    """
    
    df = pd.read_sql_query(query, conn, params=(limit,))
    
    # Convert to JSON
    data = df.to_dict('records')
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    conn.close()
    
    print(f"✅ Exported {len(df):,} records to {output_file}")
    return output_file

def export_summary_stats():
    """Export summary statistics"""
    print("Creating summary statistics file...")
    
    conn = sqlite3.connect('SML_STEM_IoT.db')
    
    # Get summary data
    queries = {
        'total_records': "SELECT COUNT(*) as count FROM data",
        'records_by_sensor': "SELECT sensor, COUNT(*) as count FROM data GROUP BY sensor ORDER BY sensor",
        'records_by_parameter': "SELECT parameter, COUNT(*) as count FROM data GROUP BY parameter ORDER BY parameter",
        'time_range': "SELECT MIN(timestamp) as min_time, MAX(timestamp) as max_time FROM data",
        'avg_values_by_parameter': """
            SELECT parameter, 
                   AVG(value) as avg_value,
                   MIN(value) as min_value,
                   MAX(value) as max_value,
                   COUNT(*) as count
            FROM data 
            GROUP BY parameter
        """
    }
    
    summary = {}
    for name, query in queries.items():
        df = pd.read_sql_query(query, conn)
        summary[name] = df.to_dict('records')
    
    # Save summary
    with open('iot_data_summary.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    conn.close()
    
    print("✅ Created iot_data_summary.json")
    return 'iot_data_summary.json'

def main():
    """Main export function with menu"""
    print("IoT Data Export Tool")
    print("====================")
    print("Database contains 1,601,020 records")
    print()
    
    print("Available export options:")
    print("1. Export all data to single CSV file")
    print("2. Export data separated by sensor (3 files)")
    print("3. Export data separated by parameter (4 files)")
    print("4. Export sample data to JSON (10,000 records)")
    print("5. Export summary statistics")
    print("6. Export everything")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == '1':
        export_to_csv()
    elif choice == '2':
        export_by_sensor()
    elif choice == '3':
        export_by_parameter()
    elif choice == '4':
        export_to_json()
    elif choice == '5':
        export_summary_stats()
    elif choice == '6':
        print("Exporting everything...")
        export_to_csv()
        export_by_sensor()
        export_by_parameter()
        export_to_json()
        export_summary_stats()
        print("\n🎉 All exports completed!")
    else:
        print("Invalid choice. Running default: export all to CSV")
        export_to_csv()

if __name__ == "__main__":
    main() 