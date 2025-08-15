import sqlite3
import pandas as pd
from datetime import datetime

def connect_db():
    """Connect to the SQLite database"""
    return sqlite3.connect('SML_STEM_IoT.db')

def get_all_tables():
    """Get list of all tables in the database"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]
    conn.close()
    return tables

def get_sensors():
    """Get list of all sensors"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT sensor FROM data ORDER BY sensor;")
    sensors = [row[0] for row in cursor.fetchall()]
    conn.close()
    return sensors

def get_parameters():
    """Get list of all measured parameters"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT parameter FROM data ORDER BY parameter;")
    parameters = [row[0] for row in cursor.fetchall()]
    conn.close()
    return parameters

def query_data(sensor=None, parameter=None, limit=100):
    """Query data with optional filters"""
    conn = connect_db()
    
    query = "SELECT * FROM data WHERE 1=1"
    params = []
    
    if sensor is not None:
        query += " AND sensor = ?"
        params.append(sensor)
    
    if parameter is not None:
        query += " AND parameter = ?"
        params.append(parameter)
    
    query += f" ORDER BY timestamp DESC LIMIT {limit}"
    
    # Use pandas for better display
    df = pd.read_sql_query(query, conn, params=params)
    
    # Convert timestamp to readable format
    if not df.empty:
        df['readable_time'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    conn.close()
    return df

def get_summary_stats():
    """Get summary statistics for the database"""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Total records
    cursor.execute("SELECT COUNT(*) FROM data;")
    total_records = cursor.fetchone()[0]
    
    # Time range
    cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM data;")
    time_range = cursor.fetchone()
    
    # Records per sensor
    cursor.execute("SELECT sensor, COUNT(*) FROM data GROUP BY sensor;")
    sensor_counts = cursor.fetchall()
    
    # Records per parameter
    cursor.execute("SELECT parameter, COUNT(*) FROM data GROUP BY parameter;")
    parameter_counts = cursor.fetchall()
    
    conn.close()
    
    print(f"Database Summary:")
    print(f"Total records: {total_records:,}")
    print(f"Time range: {datetime.fromtimestamp(time_range[0]/1000)} to {datetime.fromtimestamp(time_range[1]/1000)}")
    print(f"\nRecords per sensor:")
    for sensor, count in sensor_counts:
        print(f"  Sensor {sensor}: {count:,} records")
    print(f"\nRecords per parameter:")
    for param, count in parameter_counts:
        print(f"  {param}: {count:,} records")

# Example usage functions
def example_queries():
    """Show example queries"""
    print("=== Example Queries ===\n")
    
    # Latest CO2 readings
    print("Latest 10 CO2 readings:")
    co2_data = query_data(parameter='CO2', limit=10)
    print(co2_data[['sensor', 'parameter', 'value', 'readable_time']])
    print()
    
    # All data from sensor 3
    print("Latest 5 readings from sensor 3:")
    sensor3_data = query_data(sensor=3, limit=5)
    print(sensor3_data[['sensor', 'parameter', 'value', 'readable_time']])
    print()

if __name__ == "__main__":
    print("IoT Database Reader")
    print("==================")
    
    # Show summary
    get_summary_stats()
    print()
    
    # Show available options
    print("Available sensors:", get_sensors())
    print("Available parameters:", get_parameters())
    print()
    
    # Show examples
    example_queries()
    
    print("\n=== How to use this script ===")
    print("1. Import the functions: from db_reader import query_data, get_summary_stats")
    print("2. Query specific data: df = query_data(sensor=3, parameter='CO2', limit=50)")
    print("3. Get summary: get_summary_stats()") 