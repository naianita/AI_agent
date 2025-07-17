import os
import csv
from datetime import datetime
from typing import Dict, List, Optional
import statistics

def analyze_historical_air_quality(parameter: str = "CO2", hours: int = 24) -> str:
    """Analyze historical air quality data from PT file for specific parameters"""
    file_path = r'c:\Users\USER\OneDrive\文件\capstone\PT_202505011759.txt'
    
    if not os.path.exists(file_path):
        return "Historical air quality data file not found."
    
    try:
        # Read and parse historical data
        data_points = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f):
                if line_num > 10000:  # Limit for performance
                    break
                
                parts = line.strip().split(', ')
                if len(parts) >= 6:
                    # Parse: ID, Time, Code, Label, Unit, Value
                    label = parts[3].split(': ')[1] if ': ' in parts[3] else ''
                    if label.upper() == parameter.upper():
                        try:
                            time_str = parts[1].split(': ')[1]
                            value_str = parts[5].split(': ')[1]
                            value = float(value_str)
                            data_points.append({
                                'time': time_str,
                                'value': value,
                                'unit': parts[4].split(': ')[1] if ': ' in parts[4] else ''
                            })
                        except (ValueError, IndexError):
                            continue
        
        if not data_points:
            return f"No historical data found for {parameter}."
        
        # Analyze the data
        values = [dp['value'] for dp in data_points]
        unit = data_points[0]['unit'] if data_points else ''
        
        analysis = f"📊 **Historical {parameter} Analysis** (Sample: {len(data_points):,} points)\n\n"
        analysis += f"**Statistics:**\n"
        analysis += f"  • Average: {statistics.mean(values):.2f} {unit}\n"
        analysis += f"  • Minimum: {min(values):.2f} {unit}\n"
        analysis += f"  • Maximum: {max(values):.2f} {unit}\n"
        analysis += f"  • Median: {statistics.median(values):.2f} {unit}\n"
        analysis += f"  • Std Deviation: {statistics.stdev(values):.2f} {unit}\n"
        
        # Air quality assessment for CO2
        if parameter.upper() == 'CO2':
            avg_co2 = statistics.mean(values)
            analysis += f"\n**Air Quality Assessment:**\n"
            if avg_co2 < 400:
                analysis += f"  • Excellent air quality ({avg_co2:.0f} ppm average)\n"
            elif avg_co2 < 600:
                analysis += f"  • Good air quality ({avg_co2:.0f} ppm average)\n"
            elif avg_co2 < 800:
                analysis += f"  • Moderate air quality ({avg_co2:.0f} ppm average)\n"
            else:
                analysis += f"  • Poor air quality ({avg_co2:.0f} ppm average) - Ventilation recommended\n"
        
        # Show recent readings
        analysis += f"\n**Recent Readings:**\n"
        for i, dp in enumerate(data_points[:5]):
            analysis += f"  • {dp['time']}: {dp['value']} {unit}\n"
        
        return analysis
        
    except Exception as e:
        return f"Error analyzing historical data: {str(e)}"

def compare_historical_vs_current(parameter: str = "CO2") -> str:
    """Compare historical air quality data with current IoT sensor readings"""
    # Get historical data
    historical_data = get_historical_parameter_data(parameter)
    current_data = get_current_parameter_data(parameter)
    
    if not historical_data or not current_data:
        return f"Insufficient data for {parameter} comparison."
    
    hist_avg = statistics.mean(historical_data)
    curr_avg = statistics.mean(current_data)
    
    comparison = f"🔄 **Historical vs Current {parameter} Comparison**\n\n"
    comparison += f"**Historical Data (May 2025):**\n"
    comparison += f"  • Average: {hist_avg:.2f}\n"
    comparison += f"  • Range: {min(historical_data):.2f} - {max(historical_data):.2f}\n"
    comparison += f"  • Sample size: {len(historical_data):,} readings\n\n"
    
    comparison += f"**Current Data (Recent):**\n"
    comparison += f"  • Average: {curr_avg:.2f}\n"
    comparison += f"  • Range: {min(current_data):.2f} - {max(current_data):.2f}\n"
    comparison += f"  • Sample size: {len(current_data):,} readings\n\n"
    
    # Calculate difference
    diff = curr_avg - hist_avg
    diff_percent = (diff / hist_avg) * 100 if hist_avg != 0 else 0
    
    comparison += f"**Change Analysis:**\n"
    if diff > 0:
        comparison += f"  • Current levels are {diff:.2f} ({diff_percent:+.1f}%) HIGHER than historical\n"
    else:
        comparison += f"  • Current levels are {abs(diff):.2f} ({diff_percent:+.1f}%) LOWER than historical\n"
    
    # Provide recommendations
    if parameter.upper() == 'CO2':
        if curr_avg > hist_avg + 100:
            comparison += f"  • 💡 Recommendation: Current CO2 levels significantly elevated - increase ventilation\n"
        elif curr_avg < hist_avg - 100:
            comparison += f"  • ✅ Good: Current CO2 levels improved compared to historical data\n"
    
    return comparison

def get_air_quality_recommendations() -> str:
    """Provide personalized air quality recommendations based on both datasets"""
    try:
        # Get current environmental status
        current_co2 = get_current_average_parameter('CO2')
        current_temp = get_current_average_parameter('Temperature')
        current_humidity = get_current_average_parameter('Humidity')
        current_tvoc = get_current_average_parameter('TVOC')
        
        recommendations = "💡 **Personalized Air Quality Recommendations**\n\n"
        
        # CO2 recommendations
        if current_co2:
            if current_co2 > 1000:
                recommendations += "🌬️ **Immediate Action Required:**\n"
                recommendations += "  • Open windows or increase ventilation immediately\n"
                recommendations += "  • CO2 levels are dangerously high for indoor spaces\n\n"
            elif current_co2 > 800:
                recommendations += "⚠️ **Ventilation Recommended:**\n"
                recommendations += "  • Consider opening windows or using fans\n"
                recommendations += "  • Monitor levels and improve air circulation\n\n"
            else:
                recommendations += "✅ **CO2 Levels Good:**\n"
                recommendations += "  • Current ventilation appears adequate\n\n"
        
        # Temperature recommendations
        if current_temp:
            if current_temp > 26:
                recommendations += "🌡️ **Temperature Control:**\n"
                recommendations += "  • Consider cooling the space for optimal comfort\n"
                recommendations += "  • High temperatures can increase TVOC emissions\n\n"
            elif current_temp < 20:
                recommendations += "🌡️ **Temperature Control:**\n"
                recommendations += "  • Consider heating for optimal comfort range (20-24°C)\n\n"
        
        # Humidity recommendations
        if current_humidity:
            if current_humidity > 60:
                recommendations += "💧 **Humidity Control:**\n"
                recommendations += "  • High humidity detected - use dehumidifier\n"
                recommendations += "  • Monitor for mold/mildew risk\n\n"
            elif current_humidity < 30:
                recommendations += "💧 **Humidity Control:**\n"
                recommendations += "  • Low humidity - consider humidifier\n"
                recommendations += "  • Dry air can cause discomfort\n\n"
        
        # TVOC recommendations
        if current_tvoc and current_tvoc > 30:
            recommendations += "🏠 **Indoor Air Quality:**\n"
            recommendations += "  • Elevated TVOC levels detected\n"
            recommendations += "  • Check for sources: cleaning products, furniture, paint\n"
            recommendations += "  • Increase ventilation to reduce chemical concentrations\n\n"
        
        recommendations += "📱 **General Tips:**\n"
        recommendations += "  • Monitor trends regularly using this system\n"
        recommendations += "  • Maintain good ventilation especially during cooking/cleaning\n"
        recommendations += "  • Consider air purifiers for consistently high TVOC levels\n"
        
        return recommendations
        
    except Exception as e:
        return f"Error generating recommendations: {str(e)}"

def get_historical_parameter_data(parameter: str, max_lines: int = 5000) -> List[float]:
    """Extract historical data for a specific parameter from PT file"""
    file_path = r'c:\Users\USER\OneDrive\文件\capstone\PT_202505011759.txt'
    values = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f):
                if line_num > max_lines:
                    break
                
                parts = line.strip().split(', ')
                if len(parts) >= 6:
                    label = parts[3].split(': ')[1] if ': ' in parts[3] else ''
                    if label.upper() == parameter.upper():
                        try:
                            value_str = parts[5].split(': ')[1]
                            value = float(value_str)
                            values.append(value)
                        except (ValueError, IndexError):
                            continue
        return values
    except:
        return []

def get_current_parameter_data(parameter: str) -> List[float]:
    """Extract current data for a specific parameter from IoT database"""
    import sqlite3
    
    db_path = r'c:\Users\USER\OneDrive\文件\capstone\SML_STEM_IoT.db'
    values = []
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get recent data (last 1000 readings)
        cursor.execute("""
            SELECT value FROM data 
            WHERE parameter = ? 
            ORDER BY timestamp DESC 
            LIMIT 1000;
        """, (parameter,))
        
        results = cursor.fetchall()
        values = [row[0] for row in results]
        conn.close()
        
    except:
        pass
    
    return values

def get_current_average_parameter(parameter: str) -> Optional[float]:
    """Get current average value for a parameter"""
    import sqlite3
    
    db_path = r'c:\Users\USER\OneDrive\文件\capstone\SML_STEM_IoT.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT AVG(value) FROM data 
            WHERE parameter = ? 
            AND timestamp > (SELECT MAX(timestamp) - 3600000 FROM data WHERE parameter = ?);
        """, (parameter, parameter))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result and result[0] else None
    except:
        return None 