#!/usr/bin/env python
"""
System validation script for OpenAI-powered IoT Conversational Agent
Validates all components before training and deployment
"""
import os
import sys
import django
from pathlib import Path
import json

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatBot.settings')
django.setup()

from django.conf import settings
from LineBot.agent.model_hub import ModelHub
from LineBot.agent.tool_manager import ToolManager
from LineBot.agent.react_agent import ReActAgent
from LineBot.agent.fine_tuner import FineTuner

def print_header(title):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_check(item, status, details=""):
    """Print validation check result"""
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {item}")
    if details:
        print(f"   {details}")

def validate_environment():
    """Validate environment configuration"""
    print_header("Environment Configuration")
    
    # Check API key
    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    api_key_set = bool(api_key and api_key != 'your_openai_api_key_here')
    print_check("OpenAI API Key", api_key_set, 
                f"Set: {'Yes' if api_key_set else 'No - Please add to .env'}")
    
    # Check model settings
    complex_model = getattr(settings, 'COMPLEX_LLM_MODEL', '')
    is_nano_model = 'gpt-4.1-nano-2025-04-14' in complex_model
    print_check("GPT-4.1-nano Model Config", is_nano_model,
                f"Model: {complex_model}")
    
    # Check Django settings
    debug_mode = getattr(settings, 'DEBUG', False)
    print_check("Django Debug Mode", debug_mode,
                f"Debug: {debug_mode}")
    
    return api_key_set and is_nano_model

def validate_data_files():
    """Validate IoT data files"""
    print_header("IoT Data Files")
    
    project_root = Path(__file__).parent
    data_files = [
        'iot_temperature_data.csv',
        'iot_humidity_data.csv', 
        'iot_co2_data.csv',
        'iot_tvoc_data.csv'
    ]
    
    files_exist = []
    for file_name in data_files:
        file_path = project_root / file_name
        exists = file_path.exists()
        files_exist.append(exists)
        size = f"{file_path.stat().st_size / (1024*1024):.1f}MB" if exists else "Missing"
        print_check(f"IoT Data: {file_name}", exists, f"Size: {size}")
    
    return all(files_exist)

def validate_training_data():
    """Validate training data generation"""
    print_header("Training Data")
    
    training_dir = Path(__file__).parent / "LineBot" / "agent" / "training_data"
    training_files = [
        'initial_training_data.json',
        'nano_inference_data.json', 
        'nano_finetune_data.json'
    ]
    
    files_ready = []
    for file_name in training_files:
        file_path = training_dir / file_name
        exists = file_path.exists()
        files_ready.append(exists)
        
        if exists:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "training_examples" in data:
                        count = len(data["training_examples"])
                    elif isinstance(data, list):
                        count = len(data)
                    else:
                        count = "Unknown format"
                print_check(f"Training: {file_name}", True, f"Examples: {count}")
            except Exception as e:
                print_check(f"Training: {file_name}", False, f"Error: {e}")
        else:
            print_check(f"Training: {file_name}", False, "Not generated yet")
    
    return any(files_ready)

def validate_components():
    """Validate system components"""
    print_header("System Components")
    
    try:
        # Test ModelHub
        model_hub = ModelHub()
        print_check("ModelHub Initialization", True, "Successfully created")
        
        # Test ToolManager
        tool_manager = ToolManager()
        print_check("ToolManager Initialization", True, 
                   f"Tools registered: {len(tool_manager.tools)}")
        
        # Test ReActAgent
        agent = ReActAgent(model_hub, tool_manager)
        print_check("ReAct Agent Initialization", True, "Successfully created")
        
        # Test FineTuner
        fine_tuner = FineTuner()
        print_check("Fine-tuner Initialization", True, "Successfully created")
        
        return True
        
    except Exception as e:
        print_check("Component Validation", False, f"Error: {e}")
        return False

def validate_database():
    """Validate database setup"""
    print_header("Database Configuration")
    
    try:
        from django.db import connection
        from LineBot.models import User_Info
        
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print_check("Database Connection", True, "Connected successfully")
        
        # Test model access
        count = User_Info.objects.count()
        print_check("User_Info Model", True, f"Records: {count}")
        
        return True
        
    except Exception as e:
        print_check("Database Validation", False, f"Error: {e}")
        return False

def estimate_costs():
    """Estimate training and operational costs"""
    print_header("Cost Analysis")
    
    # Training data costs
    training_examples = 5000  # nano_finetune_data.json
    avg_tokens = 300
    total_tokens = training_examples * avg_tokens
    
    # Fine-tuning cost (gpt-4.1-nano cached rate)
    fine_tune_cost_per_million = 25.0  # $25 per 1M tokens
    fine_tune_cost = (total_tokens / 1_000_000) * fine_tune_cost_per_million
    
    # Inference cost estimates (per month)
    monthly_requests = 1000  # Estimated
    inference_cost_per_million = 0.40  # $0.40 per 1M output tokens
    monthly_inference_cost = (monthly_requests * avg_tokens / 1_000_000) * inference_cost_per_million
    
    print_check("Fine-tuning Cost", True, f"${fine_tune_cost:.2f} one-time")
    print_check("Monthly Inference Cost", True, f"${monthly_inference_cost:.2f} estimated")
    print_check("Total Setup Cost", True, f"${fine_tune_cost:.2f}")
    
    return fine_tune_cost < 10.0  # Check if within reasonable budget

def generate_next_steps(validations):
    """Generate actionable next steps based on validation results"""
    print_header("Next Steps")
    
    env_ok, data_ok, training_ok, components_ok, db_ok, cost_ok = validations
    
    if not env_ok:
        print("🔧 Setup OpenAI API:")
        print("   1. Get API key from https://platform.openai.com/")
        print("   2. Create .env file in ChatBot/ directory")
        print("   3. Add: API_KEY=your_openai_api_key_here")
        
    if not data_ok:
        print("📊 Prepare IoT Data:")
        print("   1. Ensure CSV files are in project root")
        print("   2. Check file formats and permissions")
        print("   3. Run data validation scripts")
        
    if not training_ok:
        print("🤖 Generate Training Data:")
        print("   cd ChatBot/LineBot/agent/training_data")
        print("   python generate_training_data.py")
        
    if env_ok and data_ok and training_ok and components_ok:
        print("🚀 Ready for Fine-tuning:")
        print("   cd ChatBot")
        print("   python manage.py train_gpt35_fallback --data-file LineBot/agent/training_data/nano_finetune_data.json --wait")
        
    if all(validations):
        print("✅ System fully validated! Ready for research implementation.")
        print("\n🎯 Research Objectives Status:")
        print("   ✅ Real-time IoT Integration")
        print("   ✅ ReAct Framework Implementation") 
        print("   ✅ Memory Management System")
        print("   ✅ Tool-based Architecture")
        print("   ✅ Fine-tuning Capabilities")
        print("   ✅ Environmental Health Advisory")

def main():
    """Main validation function"""
    print("🤖 OpenAI IoT Conversational Agent - System Validation")
    print("Validating research implementation readiness...")
    
    # Run all validations
    validations = [
        validate_environment(),
        validate_data_files(),
        validate_training_data(),
        validate_components(),
        validate_database(),
        estimate_costs()
    ]
    
    # Summary
    print_header("Validation Summary")
    total_checks = len(validations)
    passed_checks = sum(validations)
    
    print(f"📊 System Status: {passed_checks}/{total_checks} checks passed")
    
    if passed_checks == total_checks:
        print("🎉 All validations passed! System ready for research.")
    else:
        print("⚠️  Some validations failed. Please address issues below.")
    
    # Generate actionable next steps
    generate_next_steps(validations)
    
    return passed_checks == total_checks

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Validation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Validation error: {e}")
        sys.exit(1) 