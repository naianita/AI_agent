# This is a mock implementation - replace with actual IoT integration
import json
from typing import Dict, Any
import sqlite3
import os
from datetime import datetime, timedelta
import statistics

# Mock device states
device_states = {
    "lights": {"status": "off", "brightness": 0},
    "temperature": {"indoor": 25, "outdoor": 28},
    "door": {"status": "closed"},
    "window": {"status": "closed"}
}

def get_device_status(device_name: str) -> str:
    """Get the status of a smart home device"""
    if device_name in device_states:
        return json.dumps(device_states[device_name])
    else:
        return f"Device '{device_name}' not found"

def control_light(action: str, brightness: int = 100) -> str:
    """Control smart lights"""
    if action == "on":
        device_states["lights"]["status"] = "on"
        device_states["lights"]["brightness"] = brightness
        return f"Lights turned on at {brightness}% brightness"
    elif action == "off":
        device_states["lights"]["status"] = "off"
        device_states["lights"]["brightness"] = 0
        return "Lights turned off"
    else:
        return "Invalid action. Use 'on' or 'off'"

def get_temperature() -> str:
    """Get current temperature readings"""
    indoor = device_states["temperature"]["indoor"]
    outdoor = device_states["temperature"]["outdoor"]
    return f"Indoor: {indoor}°C, Outdoor: {outdoor}°C"

def control_door(action: str) -> str:
    """Control smart door"""
    if action in ["open", "close"]:
        device_states["door"]["status"] = "open" if action == "open" else "closed"
        return f"Door {action}d successfully"
    else:
        return "Invalid action. Use 'open' or 'close'"

def get_current_environmental_status() -> str:
    """Get current environmental readings from all IoT sensors"""
    db_path = r'c:\Users\USER\OneDrive\文件\capstone\SML_STEM_IoT.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get latest readings for each parameter from all sensors
        cursor.execute("""
            SELECT sensor, parameter, value, datetime(timestamp/1000, 'unixepoch') as readable_time
            FROM data 
            WHERE (sensor, parameter, timestamp) IN (
                SELECT sensor, parameter, MAX(timestamp)
                FROM data 
                GROUP BY sensor, parameter
            )
            ORDER BY sensor, parameter;
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return "No current environmental data available."
        
        # Organize by sensor
        sensors_data = {}
        for sensor, param, value, time in results:
            if sensor not in sensors_data:
                sensors_data[sensor] = {}
            sensors_data[sensor][param] = {'value': value, 'time': time}
        
        # Format response
        status = "🏠 **Current Environmental Status**\n\n"
        for sensor_id, params in sensors_data.items():
            status += f"**Sensor {sensor_id}:**\n"
            for param, data in params.items():
                unit = get_unit_for_parameter(param)
                status += f"  • {param}: {data['value']}{unit} (as of {data['time']})\n"
            status += "\n"
        
        # Add air quality assessment
        status += get_air_quality_assessment(sensors_data)
        
        return status
        
    except Exception as e:
        return f"Error retrieving environmental data: {str(e)}"

def get_environmental_trends(hours: int = 24) -> str:
    """Get environmental trends over the last N hours"""
    db_path = r'c:\Users\USER\OneDrive\文件\capstone\SML_STEM_IoT.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Calculate timestamp for N hours ago
        hours_ago_ms = int((datetime.now().timestamp() - (hours * 3600)) * 1000)
        
        cursor.execute("""
            SELECT parameter, AVG(value) as avg_value, MIN(value) as min_value, 
                   MAX(value) as max_value, COUNT(*) as count
            FROM data 
            WHERE timestamp > ?
            GROUP BY parameter
            ORDER BY parameter;
        """, (hours_ago_ms,))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return f"No environmental data available for the last {hours} hours."
        
        trends = f"📈 **Environmental Trends (Last {hours} hours)**\n\n"
        for param, avg_val, min_val, max_val, count in results:
            unit = get_unit_for_parameter(param)
            trends += f"**{param}:**\n"
            trends += f"  • Average: {avg_val:.1f}{unit}\n"
            trends += f"  • Range: {min_val:.1f} - {max_val:.1f}{unit}\n"
            trends += f"  • Data points: {count:,}\n\n"
        
        return trends
        
    except Exception as e:
        return f"Error retrieving trend data: {str(e)}"

def check_environmental_alerts() -> str:
    """Check for environmental alerts based on thresholds"""
    db_path = r'c:\Users\USER\OneDrive\文件\capstone\SML_STEM_IoT.db'
    
    # Define thresholds
    thresholds = {
        'CO2': {'warning': 800, 'critical': 1200},
        'Temperature': {'low': 18, 'high': 28},
        'Humidity': {'low': 30, 'high': 60},
        'TVOC': {'warning': 50, 'critical': 100}
    }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get latest readings
        cursor.execute("""
            SELECT sensor, parameter, value, datetime(timestamp/1000, 'unixepoch') as readable_time
            FROM data 
            WHERE (sensor, parameter, timestamp) IN (
                SELECT sensor, parameter, MAX(timestamp)
                FROM data 
                GROUP BY sensor, parameter
            )
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        alerts = []
        for sensor, param, value, time in results:
            if param in thresholds:
                threshold = thresholds[param]
                
                if param == 'CO2':
                    if value >= threshold['critical']:
                        alerts.append(f"🚨 CRITICAL: Sensor {sensor} CO2 level is {value} ppm (>= {threshold['critical']})")
                    elif value >= threshold['warning']:
                        alerts.append(f"⚠️ WARNING: Sensor {sensor} CO2 level is {value} ppm (>= {threshold['warning']})")
                
                elif param == 'Temperature':
                    if value <= threshold['low']:
                        alerts.append(f"🌡️ LOW: Sensor {sensor} temperature is {value}°C (<= {threshold['low']})")
                    elif value >= threshold['high']:
                        alerts.append(f"🌡️ HIGH: Sensor {sensor} temperature is {value}°C (>= {threshold['high']})")
                
                elif param == 'Humidity':
                    if value <= threshold['low']:
                        alerts.append(f"💧 LOW: Sensor {sensor} humidity is {value}% (<= {threshold['low']})")
                    elif value >= threshold['high']:
                        alerts.append(f"💧 HIGH: Sensor {sensor} humidity is {value}% (>= {threshold['high']})")
                
                elif param == 'TVOC':
                    if value >= threshold['critical']:
                        alerts.append(f"🚨 CRITICAL: Sensor {sensor} TVOC level is {value} (>= {threshold['critical']})")
                    elif value >= threshold['warning']:
                        alerts.append(f"⚠️ WARNING: Sensor {sensor} TVOC level is {value} (>= {threshold['warning']})")
        
        if alerts:
            return "🚨 **Environmental Alerts**\n\n" + "\n".join(alerts)
        else:
            return "✅ **All Environmental Parameters Normal**\n\nNo alerts detected. All sensors reading within normal ranges."
            
    except Exception as e:
        return f"Error checking environmental alerts: {str(e)}"

def compare_sensors() -> str:
    """Compare readings across different sensors"""
    db_path = r'c:\Users\USER\OneDrive\文件\capstone\SML_STEM_IoT.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get latest readings for comparison
        cursor.execute("""
            SELECT sensor, parameter, value
            FROM data 
            WHERE (sensor, parameter, timestamp) IN (
                SELECT sensor, parameter, MAX(timestamp)
                FROM data 
                GROUP BY sensor, parameter
            )
            ORDER BY parameter, sensor;
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        # Organize by parameter
        param_data = {}
        for sensor, param, value in results:
            if param not in param_data:
                param_data[param] = {}
            param_data[param][sensor] = value
        
        comparison = "⚖️ **Sensor Comparison**\n\n"
        for param, sensors in param_data.items():
            if len(sensors) > 1:
                unit = get_unit_for_parameter(param)
                values = list(sensors.values())
                avg_val = statistics.mean(values)
                std_dev = statistics.stdev(values) if len(values) > 1 else 0
                
                comparison += f"**{param}:**\n"
                for sensor_id, value in sorted(sensors.items()):
                    diff_from_avg = value - avg_val
                    comparison += f"  • Sensor {sensor_id}: {value}{unit} ({diff_from_avg:+.1f} from avg)\n"
                comparison += f"  • Average: {avg_val:.1f}{unit}, Std Dev: {std_dev:.1f}\n\n"
        
        return comparison
        
    except Exception as e:
        return f"Error comparing sensors: {str(e)}"

def get_unit_for_parameter(param: str) -> str:
    """Get the appropriate unit for each parameter"""
    units = {
        'CO2': ' ppm',
        'Temperature': '°C',
        'Humidity': '%',
        'TVOC': ''
    }
    return units.get(param, '')

def get_air_quality_assessment(sensors_data: Dict) -> str:
    """Provide air quality assessment based on current readings"""
    # Get average values across all sensors
    all_co2 = []
    all_tvoc = []
    
    for sensor_data in sensors_data.values():
        if 'CO2' in sensor_data:
            all_co2.append(sensor_data['CO2']['value'])
        if 'TVOC' in sensor_data:
            all_tvoc.append(sensor_data['TVOC']['value'])
    
    assessment = "🌿 **Air Quality Assessment:**\n"
    
    if all_co2:
        avg_co2 = statistics.mean(all_co2)
        if avg_co2 < 400:
            assessment += f"  • CO2: Excellent ({avg_co2:.0f} ppm)\n"
        elif avg_co2 < 600:
            assessment += f"  • CO2: Good ({avg_co2:.0f} ppm)\n"
        elif avg_co2 < 800:
            assessment += f"  • CO2: Moderate ({avg_co2:.0f} ppm)\n"
        elif avg_co2 < 1200:
            assessment += f"  • CO2: Poor ({avg_co2:.0f} ppm) - Consider ventilation\n"
        else:
            assessment += f"  • CO2: Very Poor ({avg_co2:.0f} ppm) - Immediate ventilation needed\n"
    
    if all_tvoc:
        avg_tvoc = statistics.mean(all_tvoc)
        if avg_tvoc < 10:
            assessment += f"  • TVOC: Excellent ({avg_tvoc:.0f})\n"
        elif avg_tvoc < 50:
            assessment += f"  • TVOC: Good ({avg_tvoc:.0f})\n"
        else:
            assessment += f"  • TVOC: Elevated ({avg_tvoc:.0f}) - Check for sources\n"
    
    return assessment