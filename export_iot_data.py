import sqlite3
import csv
import os
from datetime import datetime

def export_all_data_to_csv():
    """Export all data to a single CSV file"""
    db_path = r'c:\Users\USER\OneDrive\文件\capstone\SML_STEM_IoT.db'
    output_file = 'iot_all_data.csv'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"Exporting all data to {output_file}...")
        
        # Query all data with readable timestamp
        cursor.execute("""
            SELECT 
                id,
                sensor,
                parameter,
                datetime(timestamp/1000, 'unixepoch') as readable_time,
                timestamp,
                value
            FROM data 
            ORDER BY timestamp DESC;
        """)
        
        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['ID', 'Sensor', 'Parameter', 'DateTime', 'Timestamp', 'Value'])
            
            # Write data in chunks to avoid memory issues
            while True:
                rows = cursor.fetchmany(10000)  # Process 10k rows at a time
                if not rows:
                    break
                writer.writerows(rows)
        
        conn.close()
        print(f"✓ Successfully exported all data to {output_file}")
        
        # Get file size
        size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"File size: {size_mb:.2f} MB")
        
    except Exception as e:
        print(f"Error exporting all data: {e}")

def export_by_sensor():
    """Export data separated by sensor"""
    db_path = r'c:\Users\USER\OneDrive\文件\capstone\SML_STEM_IoT.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of sensors
        cursor.execute("SELECT DISTINCT sensor FROM data ORDER BY sensor;")
        sensors = [row[0] for row in cursor.fetchall()]
        
        print(f"Exporting data for {len(sensors)} sensors...")
        
        for sensor_id in sensors:
            output_file = f'iot_sensor_{sensor_id}_data.csv'
            print(f"Exporting sensor {sensor_id} to {output_file}...")
            
            cursor.execute("""
                SELECT 
                    id,
                    sensor,
                    parameter,
                    datetime(timestamp/1000, 'unixepoch') as readable_time,
                    timestamp,
                    value
                FROM data 
                WHERE sensor = ?
                ORDER BY timestamp DESC;
            """, (sensor_id,))
            
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['ID', 'Sensor', 'Parameter', 'DateTime', 'Timestamp', 'Value'])
                
                while True:
                    rows = cursor.fetchmany(10000)
                    if not rows:
                        break
                    writer.writerows(rows)
            
            # Get row count and file size
            cursor.execute("SELECT COUNT(*) FROM data WHERE sensor = ?;", (sensor_id,))
            row_count = cursor.fetchone()[0]
            size_mb = os.path.getsize(output_file) / (1024 * 1024)
            print(f"  ✓ Sensor {sensor_id}: {row_count:,} records, {size_mb:.2f} MB")
        
        conn.close()
        
    except Exception as e:
        print(f"Error exporting by sensor: {e}")

def export_by_parameter():
    """Export data separated by parameter type"""
    db_path = r'c:\Users\USER\OneDrive\文件\capstone\SML_STEM_IoT.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of parameters
        cursor.execute("SELECT DISTINCT parameter FROM data ORDER BY parameter;")
        parameters = [row[0] for row in cursor.fetchall()]
        
        print(f"Exporting data for {len(parameters)} parameters...")
        
        for param in parameters:
            output_file = f'iot_{param.lower()}_data.csv'
            print(f"Exporting {param} to {output_file}...")
            
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
                ORDER BY timestamp DESC;
            """, (param,))
            
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['ID', 'Sensor', 'Parameter', 'DateTime', 'Timestamp', 'Value'])
                
                while True:
                    rows = cursor.fetchmany(10000)
                    if not rows:
                        break
                    writer.writerows(rows)
            
            # Get row count and file size
            cursor.execute("SELECT COUNT(*) FROM data WHERE parameter = ?;", (param,))
            row_count = cursor.fetchone()[0]
            size_mb = os.path.getsize(output_file) / (1024 * 1024)
            print(f"  ✓ {param}: {row_count:,} records, {size_mb:.2f} MB")
        
        conn.close()
        
    except Exception as e:
        print(f"Error exporting by parameter: {e}")

def export_summary_stats():
    """Export summary statistics to CSV"""
    db_path = r'c:\Users\USER\OneDrive\文件\capstone\SML_STEM_IoT.db'
    output_file = 'iot_summary_stats.csv'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"Creating summary statistics in {output_file}...")
        
        # Get summary stats by sensor and parameter
        cursor.execute("""
            SELECT 
                sensor,
                parameter,
                COUNT(*) as record_count,
                MIN(value) as min_value,
                MAX(value) as max_value,
                AVG(value) as avg_value,
                datetime(MIN(timestamp)/1000, 'unixepoch') as first_reading,
                datetime(MAX(timestamp)/1000, 'unixepoch') as last_reading
            FROM data 
            GROUP BY sensor, parameter
            ORDER BY sensor, parameter;
        """)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'Sensor', 'Parameter', 'Record_Count', 'Min_Value', 'Max_Value', 
                'Avg_Value', 'First_Reading', 'Last_Reading'
            ])
            
            for row in cursor.fetchall():
                # Round the average to 2 decimal places
                row_list = list(row)
                row_list[5] = round(row_list[5], 2)
                writer.writerow(row_list)
        
        conn.close()
        print(f"✓ Summary statistics exported to {output_file}")
        
    except Exception as e:
        print(f"Error creating summary: {e}")

def export_recent_data(hours=24):
    """Export recent data from last N hours"""
    db_path = r'c:\Users\USER\OneDrive\文件\capstone\SML_STEM_IoT.db'
    output_file = f'iot_recent_{hours}h_data.csv'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"Exporting data from last {hours} hours to {output_file}...")
        
        # Calculate timestamp for N hours ago (in milliseconds)
        hours_ago_ms = int((datetime.now().timestamp() - (hours * 3600)) * 1000)
        
        cursor.execute("""
            SELECT 
                id,
                sensor,
                parameter,
                datetime(timestamp/1000, 'unixepoch') as readable_time,
                timestamp,
                value
            FROM data 
            WHERE timestamp > ?
            ORDER BY timestamp DESC;
        """, (hours_ago_ms,))
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', 'Sensor', 'Parameter', 'DateTime', 'Timestamp', 'Value'])
            writer.writerows(cursor.fetchall())
        
        # Get count
        cursor.execute("SELECT COUNT(*) FROM data WHERE timestamp > ?;", (hours_ago_ms,))
        count = cursor.fetchone()[0]
        
        conn.close()
        size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"✓ Recent data: {count:,} records, {size_mb:.2f} MB")
        
    except Exception as e:
        print(f"Error exporting recent data: {e}")

def main():
    print("=== IoT Database CSV Export Tool ===\n")
    
    while True:
        print("\nChoose export option:")
        print("1. Export ALL data to single CSV")
        print("2. Export data by SENSOR (separate files)")
        print("3. Export data by PARAMETER (separate files)")
        print("4. Export SUMMARY statistics")
        print("5. Export RECENT data (last 24 hours)")
        print("6. Export ALL options")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-6): ").strip()
        
        if choice == '1':
            export_all_data_to_csv()
        elif choice == '2':
            export_by_sensor()
        elif choice == '3':
            export_by_parameter()
        elif choice == '4':
            export_summary_stats()
        elif choice == '5':
            export_recent_data()
        elif choice == '6':
            print("\nExporting all formats...")
            export_summary_stats()
            export_recent_data()
            export_by_parameter()
            export_by_sensor()
            print("\n✓ All exports completed!")
        elif choice == '0':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 