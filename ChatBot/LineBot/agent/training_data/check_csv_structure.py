import pandas as pd
import os
from pathlib import Path

def find_project_root() -> Path:
    """Find the project root directory containing the IoT data files"""
    current_dir = Path.cwd()
    while current_dir.name != "ChatBot_t" and current_dir.parent != current_dir:
        current_dir = current_dir.parent
    
    if current_dir.name != "ChatBot_t":
        raise RuntimeError("Could not find project root (ChatBot_t directory)")
    
    return current_dir

def check_csv_structure(file_path: str):
    """Check and print CSV file structure"""
    print(f"\nChecking structure of {os.path.basename(file_path)}:")
    # Read just the first few rows
    df = pd.read_csv(file_path, nrows=5)
    print("\nColumns:")
    print(df.columns.tolist())
    print("\nFirst row:")
    print(df.iloc[0])
    print("\nData types:")
    print(df.dtypes)

def main():
    project_root = find_project_root()
    files = [
        'iot_temperature_data.csv',
        'iot_humidity_data.csv',
        'iot_co2_data.csv',
        'iot_tvoc_data.csv'
    ]
    
    for file in files:
        file_path = project_root / file
        if file_path.exists():
            check_csv_structure(str(file_path))
        else:
            print(f"\nFile not found: {file}")

if __name__ == "__main__":
    main() 