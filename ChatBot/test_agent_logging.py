#!/usr/bin/env python
"""
Agent Logging Test Script

This script demonstrates the detailed logging functionality of the ReAct agent.
Administrators can run this to see how the agent thinks and processes information.

Usage:
    python test_agent_logging.py

The script will show:
- Agent initialization
- Tool registration
- Thought processes
- Action planning and execution
- Memory operations
- Response parsing

All logging output will appear in the terminal with detailed formatting.
"""

import os
import sys
import django
from pathlib import Path

# Add the ChatBot directory to Python path
chatbot_dir = Path(__file__).parent
sys.path.insert(0, str(chatbot_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatBot.settings')
django.setup()

from LineBot.agent.react_agent import ReActAgent
import logging

def test_agent_logging():
    """Test the agent with various scenarios to demonstrate logging"""
    
    print("=" * 80)
    print("🤖 AGENT LOGGING DEMONSTRATION")
    print("=" * 80)
    print("This will show detailed logs of how the agent thinks and processes information.")
    print("All logs will appear below with emojis and formatting for easy reading.")
    print("=" * 80)
    
    # Test scenarios
    test_cases = [
        {
            "name": "Simple Calculation",
            "message": "What is 25 * 4 + 10?",
            "description": "Tests basic tool usage and mathematical reasoning"
        },
        {
            "name": "Weather Query", 
            "message": "What's the weather like in Vancouver?",
            "description": "Tests API tool usage and response processing"
        },
        {
            "name": "Time Query",
            "message": "What time is it now?",
            "description": "Tests simple tool execution and response"
        },
        {
            "name": "Complex Reasoning",
            "message": "If I have a meeting at 3 PM and it takes 45 minutes to get there, what time should I leave? Also, what's the weather forecast?",
            "description": "Tests multi-step reasoning and multiple tool usage"
        },
        {
            "name": "Memory Test",
            "message": "Remember that I like coffee",
            "description": "Tests memory storage functionality"
        }
    ]
    
    # Initialize agent
    print(f"\n{'🚀 INITIALIZING AGENT':^80}")
    print("-" * 80)
    agent = ReActAgent("test_admin")
    
    # Run test cases
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'🧪 TEST CASE ' + str(i) + ': ' + test_case['name']:^80}")
        print("=" * 80)
        print(f"Description: {test_case['description']}")
        print(f"Message: {test_case['message']}")
        print("-" * 80)
        
        try:
            response = agent.process_message(test_case['message'])
            print(f"\n{'✅ FINAL RESPONSE':^80}")
            print("-" * 80)
            print(f"Response: {response}")
            
        except Exception as e:
            print(f"\n{'❌ ERROR':^80}")
            print("-" * 80)
            print(f"Error: {str(e)}")
        
        print("=" * 80)
        
        # Pause between tests for readability
        input("\nPress Enter to continue to next test case...")

    print(f"\n{'🏁 TESTING COMPLETED':^80}")
    print("=" * 80)
    print("All test cases have been executed.")
    print("Review the logs above to understand how the agent:")
    print("- Initializes and registers tools")
    print("- Processes user messages")  
    print("- Thinks through problems step by step")
    print("- Executes tools and processes observations")
    print("- Manages memory and conversations")
    print("- Parses and generates responses")
    print("=" * 80)

def test_memory_operations():
    """Test memory-specific operations"""
    print(f"\n{'💾 MEMORY OPERATIONS TEST':^80}")
    print("=" * 80)
    
    agent = ReActAgent("memory_test_user")
    
    # Add some conversations
    memory_tests = [
        "My name is John",
        "I work as a software engineer", 
        "I like Python programming",
        "My favorite color is blue"
    ]
    
    print("Adding conversations to test memory operations...")
    for msg in memory_tests:
        print(f"\nProcessing: {msg}")
        response = agent.process_message(msg)
        print(f"Response: {response[:100]}{'...' if len(response) > 100 else ''}")
    
    print("\n" + "=" * 80)
    print("Memory operations completed. Check logs above for detailed memory management.")

if __name__ == "__main__":
    print("Starting Agent Logging Demonstration...")
    print("Make sure you have:")
    print("1. Set up your OPENAI_API_KEY in .env file")
    print("2. Installed all requirements (pip install -r requirements.txt)")
    print("3. Run this from the ChatBot directory")
    print("\nStarting in 3 seconds...")
    
    import time
    time.sleep(3)
    
    try:
        test_agent_logging()
        
        # Ask if they want to test memory operations too
        print(f"\n{'❓ ADDITIONAL TESTS':^80}")
        test_memory = input("Would you like to test memory operations? (y/n): ").lower().strip()
        if test_memory in ['y', 'yes']:
            test_memory_operations()
            
    except KeyboardInterrupt:
        print(f"\n\n{'⚠️ TEST INTERRUPTED':^80}")
        print("Test interrupted by user.")
    except Exception as e:
        print(f"\n\n{'❌ UNEXPECTED ERROR':^80}")
        print(f"Error: {str(e)}")
        print("Make sure Django is properly configured and dependencies are installed.")
    
    print(f"\n{'👋 GOODBYE':^80}")
    print("Thank you for testing the agent logging system!") 