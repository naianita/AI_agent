#!/usr/bin/env python
"""
Test script for ReAct Agent
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatBot.settings')
django.setup()

from LineBot.agent.react_agent import ReActAgent

def test_agent():
    """Test the ReAct agent with basic functionality"""
    print("Testing ReAct Agent...")
    
    try:
        # Create agent
        agent = ReActAgent("test_user")
        print("✓ Agent created successfully")
        
        # Test basic conversation
        print("\nTesting basic conversation...")
        response = agent.process_message("Hello!")
        print(f"Response: {response}")
        
        # Test tool usage
        print("\nTesting tool usage...")
        response = agent.process_message("What time is it?")
        print(f"Response: {response}")
        
        # Test calculation
        print("\nTesting calculation...")
        response = agent.process_message("Calculate 15 * 23")
        print(f"Response: {response}")
        
        print("\n✓ All tests completed successfully!")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent() 