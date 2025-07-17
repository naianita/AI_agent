import pandas as pd
import json
from datetime import datetime, timedelta
import random
import numpy as np
from typing import List, Dict, Any
import os
from pathlib import Path
import sys
import re # Added for regex validation
from tqdm import tqdm
import logging
from typing import Dict, List, Any
import colorama
from colorama import Fore, Style
from example_generators import (
    generate_standard_examples,
    generate_sequential_example,
    generate_navigation_example,
    get_time_based_stats
)

# Initialize colorama
colorama.init()

def print_example(example: Dict[str, Any], index: int):
    """Print a formatted example"""
    print(f"\n{Fore.CYAN}Example #{index}:{Style.RESET_ALL}")
    print(f"{Fore.GREEN}System:{Style.RESET_ALL} {example['system']}")
    print(f"{Fore.YELLOW}User:{Style.RESET_ALL} {example['user']}")
    print(f"{Fore.MAGENTA}Assistant:{Style.RESET_ALL} {example['assistant']}")
    print("-" * 80)

def find_project_root() -> Path:
    """Find the project root directory containing the IoT data files"""
    current_dir = Path.cwd()
    
    # Look for common project root names
    project_names = ["ChatBot_t", "Chatbot_t", "chatbot_t", "ChatBot", "Chatbot"]
    
    while current_dir.parent != current_dir:
        if current_dir.name in project_names:
            return current_dir
        current_dir = current_dir.parent
    
    # If not found, try to find by looking for IoT data files
    current_dir = Path.cwd()
    while current_dir.parent != current_dir:
        # Check if IoT data files exist in this directory
        iot_files = [
            "iot_temperature_data.csv",
            "iot_humidity_data.csv", 
            "iot_co2_data.csv",
            "iot_tvoc_data.csv"
        ]
        
        if any((current_dir / file).exists() for file in iot_files):
            return current_dir
            
        current_dir = current_dir.parent
    
    raise RuntimeError("Could not find project root directory. Please ensure you're running from the correct location and IoT data files exist.")

def load_iot_data(file_path: str) -> pd.DataFrame:
    """Load IoT data from CSV file and ensure datetime index"""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Data file not found: {file_path}")
        
        print(f"Loading {os.path.basename(file_path)}...")
        
        # Read the first few lines to inspect the structure
        df = pd.read_csv(file_path, nrows=5)
        print(f"\nColumns found: {df.columns.tolist()}")
        
        # Try to identify timestamp and value columns
        timestamp_candidates = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
        value_candidates = [col for col in df.columns if 'value' in col.lower() or 'reading' in col.lower() or 'measurement' in col.lower()]
        
        # If no obvious timestamp column, try to detect datetime-like columns
        if not timestamp_candidates:
            for col in df.columns:
                try:
                    pd.to_datetime(df[col].iloc[0])
                    timestamp_candidates.append(col)
                except:
                    continue
        
        # If still no timestamp found, use the first column as index
        if not timestamp_candidates:
            print(f"No timestamp column found. Using first column as index.")
            timestamp_col = df.columns[0]
        else:
            timestamp_col = timestamp_candidates[0]
            print(f"Using '{timestamp_col}' as timestamp column")
        
        # If no obvious value column, use the last numeric column
        if not value_candidates:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                value_col = numeric_cols[-1]
                print(f"Using '{value_col}' as value column")
            else:
                raise ValueError("No numeric columns found for values")
        else:
            value_col = value_candidates[0]
            print(f"Using '{value_col}' as value column")
        
        # Now read the full file with identified columns
        df = pd.read_csv(file_path)
        
        # Convert timestamp and set index
        df['timestamp'] = pd.to_datetime(df[timestamp_col])
        df['value'] = df[value_col].astype(float)
        
        # Select only needed columns and set index
        df = df[['timestamp', 'value']].set_index('timestamp').sort_index()
        
        print(f"Successfully loaded {len(df)} records")
        print(f"Date range: {df.index.min()} to {df.index.max()}")
        print(f"Value range: {df['value'].min():.2f} to {df['value'].max():.2f}")
        return df
    
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}", file=sys.stderr)
        raise

def generate_time_variations() -> List[str]:
    """Generate different time-based query variations"""
    return [
        "now", "current", "latest",
        "today", "this morning", "this afternoon", "this evening",
        "last hour", "past hour",
        "last 24 hours", "past day",
        "this week", "past week",
        "trend", "pattern"
    ]

def generate_metric_variations() -> Dict[str, List[str]]:
    """Generate variations of metric-related phrases"""
    return {
        'temperature': [
            "temperature", "temp", "how hot", "how cold",
            "thermal conditions", "room temperature", "ambient temperature"
        ],
        'humidity': [
            "humidity", "moisture level", "humidity level",
            "air moisture", "relative humidity", "RH"
        ],
        'co2': [
            "CO2", "carbon dioxide", "CO2 level",
            "air quality", "CO2 concentration", "carbon dioxide level"
        ],
        'tvoc': [
            "TVOC", "volatile organic compounds", "VOC level",
            "air toxicity", "chemical levels", "VOC concentration"
        ]
    }

def generate_analysis_queries(metric: str, variations: List[str]) -> List[Dict[str, str]]:
    """Generate analysis-focused queries"""
    templates = [
        "What's the {metric} {time}?",
        "How is the {metric} {time}?",
        "Show me the {metric} {time}",
        "Analyze the {metric} {time}",
        "Give me a report on {metric} {time}",
        "Is the {metric} normal {time}?",
        "Should I be concerned about the {metric} {time}?",
        "What's the trend for {metric} {time}?",
        "Compare {metric} with previous {time}",
        "Explain the {metric} readings {time}"
    ]
    
    queries = []
    for template in templates:
        for var in variations:
            for time in generate_time_variations():
                query = template.format(metric=var, time=time)
                queries.append({"query": query, "type": "analysis"})
    return queries

def generate_action_queries(metric: str, variations: List[str]) -> List[Dict[str, str]]:
    """Generate action-oriented queries"""
    templates = [
        "What should I do about the {metric}?",
        "How can I improve the {metric}?",
        "Do I need to adjust the {metric}?",
        "Recommend actions for {metric}",
        "Is any intervention needed for {metric}?",
        "Help me optimize the {metric}",
        "What are the best settings for {metric}?",
        "How to maintain optimal {metric}?",
        "When should I adjust the {metric}?",
        "Give me tips about managing {metric}"
    ]
    
    queries = []
    for template in templates:
        for var in variations:
            queries.append({"query": template.format(metric=var), "type": "action"})
    return queries

def generate_response(query: Dict[str, str], data: pd.DataFrame, metric: str) -> str:
    """Generate contextual response based on query type and real data"""
    stats = get_time_based_stats(data)
    
    if query["type"] == "analysis":
        if metric == "temperature":
            return (f"The current temperature is {stats['current']:.1f}°C. "
                   f"In the past 24 hours, it has ranged from {stats['min']:.1f}°C to {stats['max']:.1f}°C. "
                   f"The average temperature has been {stats['mean']:.1f}°C. "
                   "Would you like to see a detailed trend analysis or specific recommendations?")
        
        elif metric == "humidity":
            status = "normal" if 30 <= stats['current'] <= 50 else "outside optimal range"
            return (f"The current humidity is {stats['current']:.1f}%, which is {status}. "
                   f"The 24-hour range has been {stats['min']:.1f}% to {stats['max']:.1f}%. "
                   "For reference, ideal indoor humidity is between 30-50%. "
                   "Would you like specific recommendations for maintaining optimal humidity?")
        
        elif metric == "co2":
            if stats['current'] < 1000:
                status = "good"
            elif stats['current'] < 2000:
                status = "moderate"
            else:
                status = "poor"
            return (f"The current CO2 level is {stats['current']:.0f} ppm, indicating {status} air quality. "
                   f"Levels have ranged from {stats['min']:.0f} to {stats['max']:.0f} ppm in the last 24 hours. "
                   "For reference:\n- Below 1000 ppm: Good\n- 1000-2000 ppm: Moderate\n- Above 2000 ppm: Poor")
        
        elif metric == "tvoc":
            if stats['current'] < 220:
                status = "low (good)"
            elif stats['current'] < 660:
                status = "moderate"
            elif stats['current'] < 2200:
                status = "high"
            else:
                status = "very high"
            return (f"Current TVOC level is {stats['current']:.0f} ppb, which is {status}. "
                   f"24-hour range: {stats['min']:.0f} to {stats['max']:.0f} ppb. "
                   "TVOC levels:\n- 0-220 ppb: Low\n- 220-660 ppb: Moderate\n- 660-2200 ppb: High\n- >2200 ppb: Very High")
    
    else:  # action queries
        if metric == "temperature":
            return ("Based on the current readings, here are my recommendations:\n"
                   "1. Ensure proper ventilation\n"
                   "2. Check HVAC system settings\n"
                   "3. Consider using fans or heating as needed\n"
                   "Would you like more specific advice based on your setup?")
        
        elif metric == "humidity":
            if stats['current'] > 50:
                return ("To reduce humidity, consider these actions:\n"
                       "1. Use a dehumidifier\n"
                       "2. Improve ventilation\n"
                       "3. Check for moisture sources\n"
                       "Would you like more detailed recommendations?")
            elif stats['current'] < 30:
                return ("To increase humidity, you can:\n"
                       "1. Use a humidifier\n"
                       "2. Add indoor plants\n"
                       "3. Place water containers near heat sources\n"
                       "Would you like specific product recommendations?")
        
        elif metric == "co2":
            return ("To maintain good CO2 levels:\n"
                   "1. Increase ventilation\n"
                   "2. Open windows periodically\n"
                   "3. Consider an air purifier\n"
                   "Would you like a customized ventilation schedule?")
        
        elif metric == "tvoc":
            return ("To improve air quality and reduce TVOCs:\n"
                   "1. Increase ventilation\n"
                   "2. Use air purifiers with activated carbon\n"
                   "3. Remove potential VOC sources\n"
                   "Would you like help identifying VOC sources?")

def generate_sequential_task(metrics: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Generate ALFWorld-style sequential interaction tasks"""
    tasks = [
        {
            "goal": "Optimize room comfort",
            "steps": [
                {"check": "temperature", "condition": "comfort"},
                {"check": "humidity", "condition": "optimal"},
                {"check": "co2", "condition": "fresh"},
            ],
            "success_criteria": "All parameters within comfort zones"
        },
        {
            "goal": "Improve air quality",
            "steps": [
                {"check": "co2", "condition": "baseline"},
                {"check": "tvoc", "condition": "safe"},
                {"check": "ventilation", "condition": "active"},
            ],
            "success_criteria": "Air quality indicators at healthy levels"
        },
        {
            "goal": "Prepare room for meeting",
            "steps": [
                {"check": "temperature", "condition": "meeting"},
                {"check": "co2", "condition": "fresh"},
                {"check": "humidity", "condition": "comfort"},
            ],
            "success_criteria": "Room conditions optimal for meeting"
        }
    ]
    
    selected_task = random.choice(tasks)
    current_state = {
        metric: get_time_based_stats(data)
        for metric, data in metrics.items()
    }
    
    interactions = []
    for step in selected_task["steps"]:
        metric = step["check"]
        if metric in current_state:
            stats = current_state[metric]
            interactions.append({
                "user": f"Check {metric} for {step['condition']} conditions",
                "assistant": generate_step_response(metric, stats, step["condition"])
            })
    
    return {
        "goal": selected_task["goal"],
        "interactions": interactions,
        "success_criteria": selected_task["success_criteria"]
    }

def generate_step_response(metric: str, stats: Dict[str, float], condition: str) -> str:
    """Generate contextual responses for sequential steps"""
    if metric == "temperature":
        if condition == "comfort":
            is_comfortable = 20 <= stats["current"] <= 25
            return (f"Current temperature is {stats['current']:.1f}°C. "
                   f"{'This is within comfort zone (20-25°C).' if is_comfortable else 'This is outside comfort zone. Adjustment needed.'} "
                   "Would you like me to suggest temperature adjustments?")
        elif condition == "meeting":
            is_optimal = 21 <= stats["current"] <= 23
            return (f"Meeting room temperature is {stats['current']:.1f}°C. "
                   f"{'This is optimal for meetings (21-23°C).' if is_optimal else 'Temperature adjustment recommended for meeting comfort.'} "
                   "Should I provide specific adjustment recommendations?")

    elif metric == "humidity":
        if condition == "optimal":
            is_optimal = 30 <= stats["current"] <= 50
            return (f"Current humidity is {stats['current']:.1f}%. "
                   f"{'This is within optimal range (30-50%).' if is_optimal else 'Humidity adjustment needed.'} "
                   "Would you like humidity control suggestions?")
        elif condition == "comfort":
            is_comfortable = 40 <= stats["current"] <= 60
            return (f"Humidity level is {stats['current']:.1f}%. "
                   f"{'This is comfortable for meetings.' if is_comfortable else 'Consider humidity adjustment for comfort.'} "
                   "Should I suggest humidity control measures?")

    elif metric == "co2":
        if condition == "fresh":
            is_fresh = stats["current"] < 800
            return (f"CO2 level is {stats['current']:.0f} ppm. "
                   f"{'Air is fresh (below 800 ppm).' if is_fresh else 'Ventilation recommended.'} "
                   "Would you like ventilation recommendations?")
        elif condition == "baseline":
            is_good = stats["current"] < 1000
            return (f"Baseline CO2 is {stats['current']:.0f} ppm. "
                   f"{'This indicates good air quality.' if is_good else 'Air quality improvement needed.'} "
                   "Should I suggest air quality improvements?")

    elif metric == "tvoc":
        if condition == "safe":
            is_safe = stats["current"] < 220
            return (f"TVOC level is {stats['current']:.0f} ppb. "
                   f"{'This indicates safe air quality.' if is_safe else 'Air quality attention needed.'} "
                   "Would you like air quality improvement suggestions?")

    return f"Checking {metric} for {condition} conditions..."

def generate_navigation_task(metrics: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Generate WebShop-style navigation interactions"""
    navigation_flows = [
        {
            "goal": "Monitor environmental conditions",
            "path": [
                {"view": "dashboard", "action": "check overview"},
                {"view": "temperature", "action": "analyze trends"},
                {"view": "air_quality", "action": "assess status"}
            ]
        },
        {
            "goal": "Manage air quality",
            "path": [
                {"view": "air_quality", "action": "check status"},
                {"view": "ventilation", "action": "adjust settings"},
                {"view": "monitoring", "action": "verify changes"}
            ]
        },
        {
            "goal": "Optimize comfort settings",
            "path": [
                {"view": "comfort", "action": "view current"},
                {"view": "controls", "action": "adjust parameters"},
                {"view": "schedule", "action": "set preferences"}
            ]
        }
    ]
    
    selected_flow = random.choice(navigation_flows)
    current_state = {
        metric: get_time_based_stats(data)
        for metric, data in metrics.items()
    }
    
    interactions = []
    for step in selected_flow["path"]:
        interactions.append({
            "user": generate_navigation_query(step),
            "assistant": generate_navigation_response(step, current_state)
        })
    
    return {
        "goal": selected_flow["goal"],
        "interactions": interactions
    }

def generate_navigation_query(step: Dict[str, str]) -> str:
    """Generate natural language queries for navigation steps"""
    templates = {
        "dashboard": [
            "Show me the dashboard overview",
            "What's the current status of all sensors?",
            "Give me a summary of environmental conditions"
        ],
        "temperature": [
            "Navigate to temperature controls",
            "Show temperature settings",
            "Open temperature monitoring page"
        ],
        "air_quality": [
            "Check air quality indicators",
            "Show air quality status",
            "Open air quality monitoring"
        ],
        "ventilation": [
            "Go to ventilation controls",
            "Show ventilation settings",
            "Access ventilation system"
        ],
        "comfort": [
            "Open comfort settings",
            "Show comfort parameters",
            "Display comfort controls"
        ],
        "controls": [
            "Access control panel",
            "Show system controls",
            "Open settings panel"
        ],
        "schedule": [
            "Go to scheduling page",
            "Show schedule settings",
            "Open time preferences"
        ],
        "monitoring": [
            "View monitoring dashboard",
            "Show sensor readings",
            "Open monitoring panel"
        ]
    }
    
    return random.choice(templates.get(step["view"], [f"Navigate to {step['view']}"]))

def generate_navigation_response(step: Dict[str, str], current_state: Dict[str, Dict[str, float]]) -> str:
    """Generate contextual responses for navigation interactions"""
    if step["view"] == "dashboard":
        return ("Here's your environmental dashboard:\n"
                f"🌡️ Temperature: {current_state['temperature']['current']:.1f}°C\n"
                f"💧 Humidity: {current_state['humidity']['current']:.1f}%\n"
                f"🌬️ CO2: {current_state['co2']['current']:.0f} ppm\n"
                f"🌿 TVOC: {current_state['tvoc']['current']:.0f} ppb\n"
                "Would you like to focus on any specific metric?")
    
    elif step["view"] == "temperature":
        temp = current_state['temperature']
        return (f"Temperature control panel:\n"
                f"Current: {temp['current']:.1f}°C\n"
                f"24h Range: {temp['min']:.1f}°C - {temp['max']:.1f}°C\n"
                f"Average: {temp['mean']:.1f}°C\n"
                "Would you like to adjust the temperature settings?")
    
    elif step["view"] == "air_quality":
        co2 = current_state['co2']
        tvoc = current_state['tvoc']
        return (f"Air quality status:\n"
                f"CO2: {co2['current']:.0f} ppm ({get_air_quality_status(co2['current'])})\n"
                f"TVOC: {tvoc['current']:.0f} ppb ({get_tvoc_status(tvoc['current'])})\n"
                "Would you like to see detailed air quality analysis?")
    
    elif step["view"] == "ventilation":
        return ("Ventilation control panel:\n"
                "1. Manual control\n"
                "2. Automatic mode\n"
                "3. Schedule settings\n"
                "Which ventilation control would you like to adjust?")
    
    elif step["view"] == "comfort":
        temp = current_state['temperature']
        humidity = current_state['humidity']
        return (f"Comfort settings panel:\n"
                f"Temperature: {temp['current']:.1f}°C (Target: 22°C)\n"
                f"Humidity: {humidity['current']:.1f}% (Target: 45%)\n"
                "Would you like to adjust comfort parameters?")
    
    return f"Navigated to {step['view']}. What would you like to do here?"

def get_air_quality_status(co2_level: float) -> str:
    if co2_level < 800:
        return "Excellent"
    elif co2_level < 1000:
        return "Good"
    elif co2_level < 1500:
        return "Fair"
    else:
        return "Poor"

def get_tvoc_status(tvoc_level: float) -> str:
    if tvoc_level < 220:
        return "Low"
    elif tvoc_level < 660:
        return "Moderate"
    elif tvoc_level < 2200:
        return "High"
    else:
        return "Very High"

def save_examples(examples: List[Dict], filename: str, output_dir: Path):
    """Save examples to a JSON file"""
    output_file = output_dir / filename
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"training_examples": examples}, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(examples)} examples to {output_file}")

def calculate_nano_costs(num_examples: int, avg_tokens: int, is_inference: bool = True) -> Dict[str, float]:
    """Calculate costs for gpt-4.1-nano model"""
    if is_inference:
        # Inference costs
        input_cost_per_million = 0.10  # $0.10 per 1M input tokens
        output_cost_per_million = 0.40  # $0.40 per 1M output tokens
    else:
        # Fine-tuning costs (using cached input rate)
        input_cost_per_million = 0.025  # $0.025 per 1M cached input tokens
        output_cost_per_million = 0.40   # $0.40 per 1M output tokens

    total_input_tokens = num_examples * avg_tokens
    estimated_output_tokens = total_input_tokens * 1.2  # Assuming 20% more tokens in output
    
    input_cost = (total_input_tokens / 1_000_000) * input_cost_per_million
    output_cost = (estimated_output_tokens / 1_000_000) * output_cost_per_million
    total_cost = input_cost + output_cost
    
    return {
        "input_tokens": total_input_tokens,
        "output_tokens": estimated_output_tokens,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost
    }

def generate_cascading_examples(initial_examples: int = 2000, final_examples: int = 5000) -> Dict[str, List[Dict[str, Any]]]:
    """Generate training examples in two phases with detailed progress"""
    try:
        # Phase 1: Generate initial examples from real data
        print(f"\n{Fore.CYAN}Phase 1: Generating initial training examples...{Style.RESET_ALL}")
        initial_distribution = {
            'standard': int(initial_examples * 0.5),    # 50% standard
            'sequential': int(initial_examples * 0.3),  # 30% sequential
            'navigation': int(initial_examples * 0.2)   # 20% navigation
        }
        
        print(f"\nDistribution:")
        for type_, count in initial_distribution.items():
            print(f"{Fore.GREEN}{type_}:{Style.RESET_ALL} {count} examples")
        
        initial_dataset = []
        example_count = 0
        
        # Generate standard examples with progress bar
        print(f"\n{Fore.YELLOW}Generating standard examples...{Style.RESET_ALL}")
        with tqdm(total=initial_distribution['standard']) as pbar:
            for metric in ["temperature", "humidity", "co2", "tvoc"]:
                examples = generate_standard_examples(
                    metric=metric,
                    count=initial_distribution['standard'] // 4,
                    data=datasets[metric]
                )
                for example in examples:
                    initial_dataset.append(example)
                    example_count += 1
                    if example_count % 10 == 0:  # Show every 10th example
                        print_example(example, example_count)
                    pbar.update(1)
        
        # Generate sequential examples
        print(f"\n{Fore.YELLOW}Generating sequential examples...{Style.RESET_ALL}")
        with tqdm(total=initial_distribution['sequential']) as pbar:
            for _ in range(initial_distribution['sequential']):
                example = generate_sequential_example(datasets)
                initial_dataset.append(example)
                example_count += 1
                if example_count % 10 == 0:
                    print_example(example, example_count)
                pbar.update(1)
        
        # Generate navigation examples
        print(f"\n{Fore.YELLOW}Generating navigation examples...{Style.RESET_ALL}")
        with tqdm(total=initial_distribution['navigation']) as pbar:
            for _ in range(initial_distribution['navigation']):
                example = generate_navigation_example(datasets)
                initial_dataset.append(example)
                example_count += 1
                if example_count % 10 == 0:
                    print_example(example, example_count)
                pbar.update(1)
        
        # Save initial dataset
        output_dir = Path(__file__).parent
        initial_file = output_dir / 'initial_training_data.json'
        with open(initial_file, 'w', encoding='utf-8') as f:
            json.dump({"training_examples": initial_dataset}, f, indent=2, ensure_ascii=False)
        
        print(f"\n{Fore.GREEN}Phase 1 Complete:{Style.RESET_ALL}")
        print(f"Generated {len(initial_dataset)} initial examples")
        print(f"Saved to: {initial_file}")
        
        # Phase 2: Generate enhanced examples
        print(f"\n{Fore.CYAN}Phase 2: Generating enhanced examples...{Style.RESET_ALL}")
        enhanced_distribution = {
            'standard': int(final_examples * 0.5),
            'sequential': int(final_examples * 0.3),
            'navigation': int(final_examples * 0.2)
        }
        
        print(f"\nEnhanced Distribution:")
        for type_, count in enhanced_distribution.items():
            print(f"{Fore.GREEN}{type_}:{Style.RESET_ALL} {count} examples")
        
        # Generate enhanced examples
        enhanced_dataset = []
        example_count = len(initial_dataset)
        
        # Standard examples
        print(f"\n{Fore.YELLOW}Generating enhanced standard examples...{Style.RESET_ALL}")
        with tqdm(total=enhanced_distribution['standard']) as pbar:
            for metric in ["temperature", "humidity", "co2", "tvoc"]:
                examples = generate_standard_examples(
                    metric=metric,
                    count=enhanced_distribution['standard'] // 4,
                    data=datasets[metric]
                )
                for example in examples:
                    enhanced_dataset.append(example)
                    example_count += 1
                    if example_count % 20 == 0:  # Show every 20th example
                        print_example(example, example_count)
                    pbar.update(1)
        
        # Sequential examples
        print(f"\n{Fore.YELLOW}Generating enhanced sequential examples...{Style.RESET_ALL}")
        with tqdm(total=enhanced_distribution['sequential']) as pbar:
            for _ in range(enhanced_distribution['sequential']):
                example = generate_sequential_example(datasets)
                enhanced_dataset.append(example)
                example_count += 1
                if example_count % 20 == 0:
                    print_example(example, example_count)
                pbar.update(1)
        
        # Navigation examples
        print(f"\n{Fore.YELLOW}Generating enhanced navigation examples...{Style.RESET_ALL}")
        with tqdm(total=enhanced_distribution['navigation']) as pbar:
            for _ in range(enhanced_distribution['navigation']):
                example = generate_navigation_example(datasets)
                enhanced_dataset.append(example)
                example_count += 1
                if example_count % 20 == 0:
                    print_example(example, example_count)
                pbar.update(1)
        
        # Save enhanced dataset
        enhanced_file = output_dir / 'enhanced_training_data.json'
        with open(enhanced_file, 'w', encoding='utf-8') as f:
            json.dump({"training_examples": enhanced_dataset}, f, indent=2, ensure_ascii=False)
        
        print(f"\n{Fore.GREEN}Phase 2 Complete:{Style.RESET_ALL}")
        print(f"Generated {len(enhanced_dataset)} enhanced examples")
        print(f"Saved to: {enhanced_file}")
        
        # Print statistics
        print(f"\n{Fore.CYAN}Generation Statistics:{Style.RESET_ALL}")
        print(f"Initial examples: {len(initial_dataset)}")
        print(f"Enhanced examples: {len(enhanced_dataset)}")
        print(f"Total examples: {len(initial_dataset) + len(enhanced_dataset)}")
        
        return {
            "initial_dataset": initial_dataset,
            "enhanced_dataset": enhanced_dataset
        }
        
    except Exception as e:
        print(f"\n{Fore.RED}Error in cascading generation: {str(e)}{Style.RESET_ALL}")
        raise

def generate_seed_prompts(distribution: Dict[str, int]) -> List[Dict[str, Any]]:
    """Generate seed prompts for the model to expand upon"""
    prompts = []
    
    # Standard query seeds
    standard_seeds = [
        "What patterns do you notice in the temperature data?",
        "How has the air quality changed over time?",
        "What's the relationship between humidity and temperature?",
        "Are there any concerning trends in the CO2 levels?",
        "How do TVOC levels vary throughout the day?"
    ]
    
    # Sequential task seeds
    sequential_seeds = [
        "Optimize the room environment for a meeting",
        "Investigate and resolve poor air quality",
        "Set up optimal conditions for overnight operation",
        "Prepare the space for high occupancy",
        "Establish energy-efficient comfort settings"
    ]
    
    # Navigation flow seeds
    navigation_seeds = [
        "Show me a complete environmental overview",
        "Help me understand the air quality metrics",
        "Guide me through the temperature control interface",
        "Navigate to the sensor configuration panel",
        "Access the historical data visualization"
    ]
    
    # Add prompts based on distribution
    prompts.extend([{"type": "standard", "seed": seed} for seed in standard_seeds])
    prompts.extend([{"type": "sequential", "seed": seed} for seed in sequential_seeds])
    prompts.extend([{"type": "navigation", "seed": seed} for seed in navigation_seeds])
    
    return prompts

def generate_enhanced_examples(
    seed_prompts: List[Dict[str, Any]],
    initial_dataset: List[Dict[str, Any]],
    distribution: Dict[str, int]
) -> List[Dict[str, Any]]:
    """Generate enhanced examples using the trained model"""
    enhanced_examples = []
    
    # Initialize model hub with the fine-tuned model
    model_hub = ModelHub()
    
    # For each seed prompt
    for prompt in seed_prompts:
        prompt_type = prompt["type"]
        target_count = distribution[prompt_type]
        
        # Generate variations using the model
        while len([ex for ex in enhanced_examples if ex["type"] == prompt_type]) < target_count:
            # Create a detailed prompt using the seed and examples from initial dataset
            context = create_generation_context(prompt, initial_dataset)
            
            # Get model's response
            response = model_hub.complex_llm_call(context)
            
            # Parse and validate the response
            new_examples = parse_model_response(response, prompt_type)
            
            # Add valid examples to the dataset
            for example in new_examples:
                if len([ex for ex in enhanced_examples if ex["type"] == prompt_type]) < target_count:
                    enhanced_examples.append(example)
    
    return enhanced_examples

def create_generation_context(prompt: Dict[str, Any], initial_dataset: List[Dict[str, Any]]) -> str:
    """Create a detailed prompt for the model to generate new examples"""
    # Select relevant examples from initial dataset
    relevant_examples = [
        ex for ex in initial_dataset 
        if ex.get("type") == prompt["type"]
    ][:3]  # Use up to 3 examples
    
    # Create the context
    context = f"""Generate new, diverse examples for IoT environmental monitoring.
Seed prompt: {prompt['seed']}
Type: {prompt['type']}

Here are some example patterns:
{json.dumps(relevant_examples, indent=2)}

Generate 3 new, unique examples following these patterns but with different scenarios, values, and responses.
Ensure the examples are realistic and use appropriate ranges for environmental metrics:
- Temperature: 18-30°C
- Humidity: 30-70%
- CO2: 400-2000 ppm
- TVOC: 0-2000 ppb

Format each example as a JSON object with 'system', 'user', and 'assistant' fields.
"""
    return context

def parse_model_response(response: str, example_type: str) -> List[Dict[str, Any]]:
    """Parse and validate the model's response"""
    try:
        # Try to parse the JSON response
        examples = json.loads(response)
        if not isinstance(examples, list):
            examples = [examples]
        
        # Validate each example
        valid_examples = []
        for example in examples:
            if validate_example(example, example_type):
                example["type"] = example_type
                valid_examples.append(example)
        
        return valid_examples
        
    except json.JSONDecodeError:
        print(f"Error parsing model response as JSON")
        return []

def validate_example(example: Dict[str, Any], example_type: str) -> bool:
    """Validate an example's format and content"""
    required_fields = ["system", "user", "assistant"]
    
    # Check required fields
    if not all(field in example for field in required_fields):
        return False
    
    # Check content is not empty
    if not all(example[field].strip() for field in required_fields):
        return False
    
    # Validate based on type
    if example_type == "standard":
        return validate_standard_example(example)
    elif example_type == "sequential":
        return validate_sequential_example(example)
    elif example_type == "navigation":
        return validate_navigation_example(example)
    
    return False

def validate_standard_example(example: Dict[str, Any]) -> bool:
    """Validate a standard query example"""
    # Check for environmental metrics
    metrics = ["temperature", "humidity", "co2", "tvoc"]
    has_metric = any(metric in example["user"].lower() for metric in metrics)
    
    # Check for numerical values in response
    has_values = bool(re.search(r'\d+(?:\.\d+)?(?:\s*[°C%ppm])', example["assistant"]))
    
    return has_metric and has_values

def validate_sequential_example(example: Dict[str, Any]) -> bool:
    """Validate a sequential task example"""
    # Check for multiple steps
    has_steps = bool(re.search(r'\d+\.|\n-|\nStep', example["assistant"]))
    
    # Check for action words
    action_words = ["check", "analyze", "measure", "adjust", "optimize"]
    has_actions = any(word in example["assistant"].lower() for word in action_words)
    
    return has_steps and has_actions

def validate_navigation_example(example: Dict[str, Any]) -> bool:
    """Validate a navigation flow example"""
    # Check for UI elements
    ui_elements = ["dashboard", "panel", "screen", "view", "page"]
    has_ui = any(element in example["assistant"].lower() for element in ui_elements)
    
    # Check for navigation words
    nav_words = ["show", "display", "navigate", "open", "go to"]
    has_nav = any(word in example["user"].lower() for word in nav_words)
    
    return has_ui and has_nav

def main():
    try:
        # Find project root and data files
        project_root = find_project_root()
        print(f"{Fore.GREEN}Project root:{Style.RESET_ALL} {project_root}")
        
        # Load and validate data files
        data_files = {
            'temperature': project_root / 'iot_temperature_data.csv',
            'humidity': project_root / 'iot_humidity_data.csv',
            'co2': project_root / 'iot_co2_data.csv',
            'tvoc': project_root / 'iot_tvoc_data.csv'
        }
        
        # Verify all files exist
        missing_files = [str(path) for path in data_files.values() if not path.exists()]
        if missing_files:
            raise FileNotFoundError(
                f"{Fore.RED}Missing data files:\n{chr(10).join(missing_files)}\n"
                f"Please ensure all data files are in the project root directory.{Style.RESET_ALL}"
            )
        
        # Load datasets with progress
        print(f"\n{Fore.CYAN}Loading data files...{Style.RESET_ALL}")
        global datasets
        datasets = {}
        for metric, file_path in tqdm(data_files.items(), desc="Loading files"):
            try:
                datasets[metric] = load_iot_data(str(file_path))
                print(f"{Fore.GREEN}Loaded {metric} data:{Style.RESET_ALL} {len(datasets[metric])} records")
            except Exception as e:
                print(f"{Fore.RED}Error loading {metric} data: {str(e)}{Style.RESET_ALL}", file=sys.stderr)
                raise
        
        # Generate examples using cascading approach
        print(f"\n{Fore.CYAN}Starting cascading example generation...{Style.RESET_ALL}")
        results = generate_cascading_examples(
            initial_examples=2000,
            final_examples=5000
        )
        
        # Calculate and display costs
        initial_tokens = len(results["initial_dataset"]) * 300
        enhanced_tokens = len(results["enhanced_dataset"]) * 300
        
        initial_cost = calculate_nano_costs(len(results["initial_dataset"]), 300, True)
        enhanced_cost = calculate_nano_costs(len(results["enhanced_dataset"]), 300, False)
        
        print(f"\n{Fore.CYAN}Cost Analysis:{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Phase 1 (Initial Training):{Style.RESET_ALL}")
        print(f"Examples: {len(results['initial_dataset'])}")
        print(f"Estimated tokens: {initial_tokens:,}")
        print(f"Estimated cost: ${initial_cost['total_cost']:.2f}")
        
        print(f"\n{Fore.YELLOW}Phase 2 (Enhanced Generation):{Style.RESET_ALL}")
        print(f"Examples: {len(results['enhanced_dataset'])}")
        print(f"Estimated tokens: {enhanced_tokens:,}")
        print(f"Estimated cost: ${enhanced_cost['total_cost']:.2f}")
        
        total_cost = initial_cost['total_cost'] + enhanced_cost['total_cost']
        print(f"\n{Fore.GREEN}Total cost: ${total_cost:.2f}{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"\n{Fore.RED}Error: {str(e)}{Style.RESET_ALL}", file=sys.stderr)
        print(f"\n{Fore.RED}Stack trace:{Style.RESET_ALL}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 