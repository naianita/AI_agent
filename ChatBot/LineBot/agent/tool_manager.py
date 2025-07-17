import inspect
import json
from typing import Dict, Callable, Any, List
import logging
from django.conf import settings
import pandas as pd
from pathlib import Path
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ToolManager:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.tool_descriptions = {}
        self.used_tools = []
        self._register_tools()
        logger.info("🔧 ToolManager initialized")
        
    def _register_tools(self):
        """Register all available tools"""
        # Data Analysis Tools
        self.register_tool(
            name="get_sensor_data",
            func=self._get_sensor_data,
            description="Get readings from specified sensor for a time range"
        )
        
        self.register_tool(
            name="analyze_trends",
            func=self._analyze_trends,
            description="Analyze trends in sensor data"
        )
        
        self.register_tool(
            name="check_thresholds",
            func=self._check_thresholds,
            description="Check if readings are within acceptable ranges"
        )
        
        self.register_tool(
            name="compare_sensors",
            func=self._compare_sensors,
            description="Compare readings between different sensors"
        )

        # Environmental Control Tools
        self.register_tool(
            name="suggest_adjustments",
            func=self._suggest_adjustments,
            description="Suggest adjustments based on current conditions"
        )
        
        self.register_tool(
            name="optimize_environment",
            func=self._optimize_environment,
            description="Optimize environmental conditions"
        )

        # Visualization Tools
        self.register_tool(
            name="generate_dashboard",
            func=self._generate_dashboard,
            description="Generate environmental dashboard"
        )
        
        self.register_tool(
            name="plot_trends",
            func=self._plot_trends,
            description="Create trend visualization"
        )
        
    def register_tool(self, name: str, func: Callable, description: str):
        """Register a new tool"""
        self.tools[name] = {
            "func": func,
            "description": description
        }
        logger.info(f"Registered tool: {name}")

    def get_tools_description(self) -> str:
        """Get description of all available tools"""
        descriptions = []
        for name, tool in self.tools.items():
            descriptions.append(f"{name}: {tool['description']}")
        return "\n".join(descriptions)
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a tool with given parameters"""
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        try:
            result = self.tools[tool_name]["func"](**parameters)
            logger.info(f"Successfully executed tool: {tool_name}")
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            raise

    def _get_sensor_data(self, sensor_type: str, time_range: str = "24h") -> pd.DataFrame:
        """Get data from specified sensor"""
        try:
            # Map sensor types to file names
            file_map = {
                "temperature": "iot_temperature_data.csv",
                "humidity": "iot_humidity_data.csv",
                "co2": "iot_co2_data.csv",
                "tvoc": "iot_tvoc_data.csv"
            }
            
            if sensor_type not in file_map:
                raise ValueError(f"Unknown sensor type: {sensor_type}")
            
            # Load data
            project_root = Path(__file__).resolve().parents[3]
            file_path = project_root / file_map[sensor_type]
            df = pd.read_csv(file_path)
            
            # Convert timestamp and filter by time range
            df['timestamp'] = pd.to_datetime(df['DateTime'])
            end_time = df['timestamp'].max()
            start_time = end_time - pd.Timedelta(time_range)
            
            return df[df['timestamp'] >= start_time]
            
        except Exception as e:
            logger.error(f"Error getting sensor data: {str(e)}")
            raise

    def _analyze_trends(self, sensor_type: str, time_range: str = "24h") -> Dict[str, Any]:
        """Analyze trends in sensor data"""
        df = self._get_sensor_data(sensor_type, time_range)
        
        # Calculate statistics
        stats = {
            "current": float(df['Value'].iloc[-1]),
            "min": float(df['Value'].min()),
            "max": float(df['Value'].max()),
            "mean": float(df['Value'].mean()),
            "std": float(df['Value'].std())
        }
        
        # Calculate trend direction
        trend = np.polyfit(range(len(df)), df['Value'], 1)[0]
        stats["trend"] = "increasing" if trend > 0 else "decreasing" if trend < 0 else "stable"
        
        return stats

    def _check_thresholds(self, sensor_type: str, time_range: str = "24h") -> Dict[str, Any]:
        """Check if readings are within acceptable ranges"""
        df = self._get_sensor_data(sensor_type, time_range)
        current_value = df['Value'].iloc[-1]
        
        # Define thresholds
        thresholds = {
            "temperature": {"min": 20, "max": 25, "unit": "°C"},
            "humidity": {"min": 30, "max": 50, "unit": "%"},
            "co2": {"min": 400, "max": 1000, "unit": "ppm"},
            "tvoc": {"min": 0, "max": 220, "unit": "ppb"}
        }
        
        threshold = thresholds[sensor_type]
        status = "normal" if threshold["min"] <= current_value <= threshold["max"] else "alert"
        
        return {
            "current_value": current_value,
            "threshold_min": threshold["min"],
            "threshold_max": threshold["max"],
            "unit": threshold["unit"],
            "status": status
        }

    def _compare_sensors(self, sensors: List[str], time_range: str = "24h") -> Dict[str, Any]:
        """Compare readings between different sensors"""
        results = {}
        for sensor in sensors:
            stats = self._analyze_trends(sensor, time_range)
            results[sensor] = stats
        return results

    def _suggest_adjustments(self, current_conditions: Dict[str, float]) -> Dict[str, str]:
        """Suggest adjustments based on current conditions"""
        suggestions = {}
        
        # Temperature adjustments
        if "temperature" in current_conditions:
            temp = current_conditions["temperature"]
            if temp < 20:
                suggestions["temperature"] = "Increase heating"
            elif temp > 25:
                suggestions["temperature"] = "Increase cooling"
        
        # Humidity adjustments
        if "humidity" in current_conditions:
            humidity = current_conditions["humidity"]
            if humidity < 30:
                suggestions["humidity"] = "Use humidifier"
            elif humidity > 50:
                suggestions["humidity"] = "Use dehumidifier"
        
        # CO2 adjustments
        if "co2" in current_conditions:
            co2 = current_conditions["co2"]
            if co2 > 1000:
                suggestions["co2"] = "Increase ventilation"
        
        # TVOC adjustments
        if "tvoc" in current_conditions:
            tvoc = current_conditions["tvoc"]
            if tvoc > 220:
                suggestions["tvoc"] = "Activate air purification"
        
        return suggestions

    def _optimize_environment(self, target_conditions: Dict[str, float]) -> Dict[str, Any]:
        """Optimize environmental conditions"""
        current_conditions = {}
        for sensor in target_conditions.keys():
            stats = self._analyze_trends(sensor, "1h")
            current_conditions[sensor] = stats["current"]
        
        adjustments = self._suggest_adjustments(current_conditions)
        
        return {
            "current_conditions": current_conditions,
            "target_conditions": target_conditions,
            "suggested_adjustments": adjustments
        }

    def _generate_dashboard(self, time_range: str = "24h") -> Dict[str, Any]:
        """Generate environmental dashboard"""
        sensors = ["temperature", "humidity", "co2", "tvoc"]
        dashboard = {}
        
        for sensor in sensors:
            dashboard[sensor] = {
                "current": self._check_thresholds(sensor, time_range),
                "trends": self._analyze_trends(sensor, time_range)
            }
        
        return dashboard

    def _plot_trends(self, sensor_type: str, time_range: str = "24h") -> Dict[str, Any]:
        """Create trend visualization data"""
        df = self._get_sensor_data(sensor_type, time_range)
        
        # Prepare data for plotting
        plot_data = {
            "timestamps": df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
            "values": df['Value'].tolist(),
            "sensor_type": sensor_type,
            "time_range": time_range
        }
        
        return plot_data