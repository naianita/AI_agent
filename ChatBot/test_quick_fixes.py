#!/usr/bin/env python
"""
Quick test to verify Phase 1 fixes work
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatBot.settings')
django.setup()

from LineBot.agent.simple_agent import SimpleAgent
from LineBot.agent.model_hub import ModelHub
from LineBot.agent.tool_manager import ToolManager

def test_fixes():
    """Quick test of key fixes"""
    print("🧪 TESTING PHASE 1 FIXES")
    print("=" * 50)
    
    try:
        # Create agent
        model_hub = ModelHub()
        tool_manager = ToolManager()
        agent = SimpleAgent(model_hub, tool_manager)
        
        # Test 1: Refusal format
        print("\n1️⃣ Testing refusal format...")
        response = agent.process_message("Play music for me")
        print(f"Response: {response[:150]}...")
        if "I don't have the capability to" in response:
            print("✅ Refusal format: FIXED")
        else:
            print("❌ Refusal format: Still broken")
        
        # Test 2: Tool usage for environmental query
        print("\n2️⃣ Testing tool usage...")
        response = agent.process_message("What's the temperature trend?")
        print(f"Response: {response[:200]}...")
        if "Tool:" in response or "historical" in response.lower():
            print("✅ Tool usage: FIXED")
        else:
            print("❌ Tool usage: Still broken")
        
        # Test 3: Reasoning depth 
        print("\n3️⃣ Testing reasoning depth...")
        response = agent.process_message("Compare recent CO2 levels to safe standards")
        print(f"Response: {response[:200]}...")
        if any(word in response.lower() for word in ["percentage", "analysis", "threshold", "ppm"]):
            print("✅ Reasoning depth: IMPROVED")
        else:
            print("❌ Reasoning depth: Needs work")
            
        print("\n" + "=" * 50)
        print("✅ Phase 1 fix testing complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_fixes() 