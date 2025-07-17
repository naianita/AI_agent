#!/usr/bin/env python
"""
Debug script to test components
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatBot.settings')
django.setup()

from LineBot.agent.model_hub import ModelHub
from LineBot.agent.tool_manager import ToolManager
from LineBot.agent.react_agent import ReActAgent

def test_components():
    """Test each component individually"""
    print("Testing ModelHub...")
    try:
        model_hub = ModelHub()
        print("✅ ModelHub created successfully")
    except Exception as e:
        print(f"❌ ModelHub error: {e}")
        return False

    print("\nTesting ToolManager...")
    try:
        tool_manager = ToolManager()
        print("✅ ToolManager created successfully")
    except Exception as e:
        print(f"❌ ToolManager error: {e}")
        return False

    print("\nTesting ReActAgent...")
    try:
        agent = ReActAgent(model_hub, tool_manager)
        print("✅ ReActAgent created successfully")
    except Exception as e:
        print(f"❌ ReActAgent error: {e}")
        return False

    print("\nTesting simple message...")
    try:
        response = agent.process_message("What's the temperature?")
        print(f"✅ Response: {response}")
    except Exception as e:
        print(f"❌ Message processing error: {e}")
        return False

    return True

if __name__ == "__main__":
    print("Starting component tests...")
    success = test_components()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed!") 