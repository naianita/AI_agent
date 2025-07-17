from typing import Dict, List, Any
import random
from datetime import datetime, timedelta
import pandas as pd

def get_time_based_stats(data: pd.DataFrame, period: str = '24H') -> Dict[str, float]:
    """Calculate statistics for a given time period"""
    try:
        # Ensure we have a DatetimeIndex
        if not isinstance(data.index, pd.DatetimeIndex):
            raise TypeError("Data must have a DatetimeIndex")
        
        # Get the most recent timestamp
        end_time = data.index.max()
        start_time = end_time - pd.Timedelta(period)
        
        # Get recent data using loc
        recent_data = data.loc[start_time:end_time]
        
        if len(recent_data) == 0:
            raise ValueError(f"No data found in the last {period}")
        
        return {
            'current': float(recent_data['value'].iloc[-1]),
            'min': float(recent_data['value'].min()),
            'max': float(recent_data['value'].max()),
            'mean': float(recent_data['value'].mean()),
            'std': float(recent_data['value'].std())
        }
    except Exception as e:
        print(f"Error calculating time-based stats: {str(e)}")
        # Return some reasonable defaults
        return {
            'current': float(data['value'].iloc[-1]),
            'min': float(data['value'].min()),
            'max': float(data['value'].max()),
            'mean': float(data['value'].mean()),
            'std': float(data['value'].std())
        }

def generate_standard_examples(metric: str, count: int, data: pd.DataFrame) -> List[Dict[str, Any]]:
    """Generate standard query examples for a specific metric"""
    examples = []
    
    # Query templates for each metric
    templates = {
        'temperature': [
            "What's the current temperature?",
            "How has the temperature changed today?",
            "Is the temperature too high?",
            "Show me temperature trends",
            "What was the highest temperature today?"
        ],
        'humidity': [
            "What's the current humidity level?",
            "Is the humidity too high?",
            "Show me humidity trends",
            "Is this humidity level comfortable?",
            "Do we need a dehumidifier?"
        ],
        'co2': [
            "What's the CO2 level now?",
            "Is the air quality good?",
            "Do we need ventilation?",
            "Show me CO2 trends",
            "Is this CO2 level safe?"
        ],
        'tvoc': [
            "What are the current TVOC levels?",
            "Are VOC levels safe?",
            "Show me TVOC trends",
            "Do we need air purification?",
            "How's the air quality?"
        ]
    }
    
    # Generate examples
    for _ in range(count):
        stats = get_time_based_stats(data)
        query = random.choice(templates.get(metric, templates['temperature']))
        
        # Generate response based on metric and stats
        if metric == 'temperature':
            response = f"The current temperature is {stats['current']:.1f}°C. "
            response += f"In the past 24 hours, it has ranged from {stats['min']:.1f}°C to {stats['max']:.1f}°C. "
            response += f"The average temperature has been {stats['mean']:.1f}°C. "
            response += "Would you like to see a detailed trend analysis?"
        
        elif metric == 'humidity':
            status = "normal" if 30 <= stats['current'] <= 50 else "outside optimal range"
            response = f"The current humidity is {stats['current']:.1f}%, which is {status}. "
            response += f"The 24-hour range has been {stats['min']:.1f}% to {stats['max']:.1f}%. "
            response += "For reference, ideal indoor humidity is between 30-50%. "
            response += "Would you like specific recommendations for maintaining optimal humidity?"
        
        elif metric == 'co2':
            if stats['current'] < 1000:
                status = "good"
            elif stats['current'] < 2000:
                status = "moderate"
            else:
                status = "poor"
            response = f"The current CO2 level is {stats['current']:.0f} ppm, indicating {status} air quality. "
            response += f"Levels have ranged from {stats['min']:.0f} to {stats['max']:.0f} ppm in the last 24 hours. "
            response += "For reference:\n- Below 1000 ppm: Good\n- 1000-2000 ppm: Moderate\n- Above 2000 ppm: Poor"
        
        else:  # tvoc
            if stats['current'] < 220:
                status = "low (good)"
            elif stats['current'] < 660:
                status = "moderate"
            elif stats['current'] < 2200:
                status = "high"
            else:
                status = "very high"
            response = f"Current TVOC level is {stats['current']:.0f} ppb, which is {status}. "
            response += f"24-hour range: {stats['min']:.0f} to {stats['max']:.0f} ppb. "
            response += "TVOC levels:\n- 0-220 ppb: Low\n- 220-660 ppb: Moderate\n- 660-2200 ppb: High\n- >2200 ppb: Very High"
        
        example = {
            "system": "You are an IoT data analysis assistant specializing in environmental monitoring.",
            "user": query,
            "assistant": response,
            "type": "standard"
        }
        examples.append(example)
    
    return examples

def generate_sequential_example(datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Generate a sequential task example"""
    tasks = [
        {
            "goal": "Optimize room comfort",
            "steps": [
                {"metric": "temperature", "target": "20-25°C"},
                {"metric": "humidity", "target": "30-50%"},
                {"metric": "co2", "target": "<1000 ppm"}
            ]
        },
        {
            "goal": "Improve air quality",
            "steps": [
                {"metric": "co2", "target": "<800 ppm"},
                {"metric": "tvoc", "target": "<220 ppb"},
                {"metric": "humidity", "target": "40-60%"}
            ]
        }
    ]
    
    task = random.choice(tasks)
    current_stats = {
        metric: get_time_based_stats(data)
        for metric, data in datasets.items()
    }
    
    response = f"I'll help you {task['goal'].lower()}. Let's check each parameter:\n\n"
    for step in task["steps"]:
        metric = step["metric"]
        if metric in current_stats:
            stats = current_stats[metric]
            response += f"1. {metric.upper()}: Current value is {stats['current']:.1f}"
            response += f" (Target: {step['target']})\n"
    
    response += "\nWould you like me to suggest specific adjustments for any parameter?"
    
    return {
        "system": f"You are an IoT assistant helping to: {task['goal']}",
        "user": f"Help me {task['goal'].lower()}",
        "assistant": response,
        "type": "sequential"
    }

def generate_navigation_example(datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Generate a navigation flow example"""
    views = [
        {
            "name": "Dashboard",
            "description": "Environmental overview showing all parameters"
        },
        {
            "name": "Analysis",
            "description": "Detailed trends and patterns"
        },
        {
            "name": "Controls",
            "description": "Adjust environmental parameters"
        }
    ]
    
    view = random.choice(views)
    stats = {
        metric: get_time_based_stats(data)
        for metric, data in datasets.items()
    }
    
    if view["name"] == "Dashboard":
        response = "Here's your environmental dashboard:\n"
        for metric, stat in stats.items():
            response += f"• {metric.upper()}: {stat['current']:.1f}"
            if metric == "temperature":
                response += "°C\n"
            elif metric == "humidity":
                response += "%\n"
            elif metric == "co2":
                response += " ppm\n"
            else:
                response += " ppb\n"
        response += "\nWhich parameter would you like to analyze in detail?"
    
    else:
        response = f"Opening the {view['name'].lower()} view. "
        response += f"This shows {view['description']}. "
        response += "What specific information would you like to see?"
    
    return {
        "system": "You are an IoT interface assistant specializing in environmental monitoring.",
        "user": f"Show me the {view['name'].lower()} view",
        "assistant": response,
        "type": "navigation"
    } 