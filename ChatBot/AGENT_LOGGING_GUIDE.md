# Agent Thought & Observation Logging System

This guide explains how to monitor and understand the agent's thought processes and decision-making through detailed logging.

## 🚀 Quick Start

### 1. Enable Logging
The logging system is already configured in `ChatBot/settings.py`. Key settings:

```python
AGENT_DEBUG_MODE = True        # Enable detailed debugging
SHOW_AGENT_THOUGHTS = True     # Show agent's thinking process
SHOW_TOOL_EXECUTIONS = True    # Show tool usage details
SHOW_OBSERVATIONS = True       # Show results and observations
```

### 2. Run the Test Script
To see the logging system in action:

```bash
cd ChatBot
python test_agent_logging.py
```

This will demonstrate various scenarios and show detailed logs.

### 3. Run the Web Interface
To see logs in real-time while using the web interface:

```bash
cd ChatBot
python manage.py runserver
```

Then open the web interface and interact with the agent. All logs will appear in the terminal.

## 📊 Understanding the Logs

### Log Categories

#### 🤖 Agent Logs (Green Background)
- Agent initialization and configuration
- Message processing start/end
- Iteration tracking through the ReAct loop
- Final answer generation

Example:
```
🤖 AGENT LOG [INFO] 2024-01-15 10:30:45
📍 LineBot.agent.react_agent
💭 📨 NEW MESSAGE RECEIVED
User: web_user
Message: What's the weather like in Vancouver?
================================================================================
```

#### 🔧 Tool Execution Logs (Blue Background)
- Tool registration and availability
- Tool execution requests and results
- Performance metrics and error handling

Example:
```
🔧 TOOL EXECUTION [INFO] 2024-01-15 10:30:46
📍 LineBot.agent.tool_manager
⚙️ 🎯 TOOL EXECUTION REQUEST
Tool: get_weather
Inputs: ['Vancouver']
Input Types: ['str']
------------------------------------------------------------
```

### Key Log Indicators

| Icon | Meaning |
|------|---------|
| 🚀 | Agent initialization |
| 📨 | New message received |
| 🔄 | Starting new iteration |
| 💭 | Agent thinking/reasoning |
| 🎯 | Action required |
| 🔧 | Tool execution |
| ✅ | Success |
| ❌ | Error |
| ⚠️ | Warning |
| 💾 | Memory operation |
| 📚 | Data retrieval |

### Thought Process Flow

1. **Message Reception**: Agent receives and processes user input
2. **Context Preparation**: Loads chat history and available tools
3. **Reasoning Loop**: Agent thinks, acts, and observes iteratively
4. **Tool Execution**: Specific tools are called based on agent's decisions
5. **Response Generation**: Final answer is formulated
6. **Memory Storage**: Conversation is saved for future reference

## 🔍 Detailed Log Analysis

### Agent Reasoning Logs
```
💭 AGENT THINKING: I need to get the current weather for Vancouver. Let me use the get_weather tool to fetch this information...
```
Shows the agent's internal reasoning process.

### Tool Execution Logs
```
🔧 EXECUTING TOOL: {"action": "get_weather", "action_inputs": ["Vancouver"]}
✅ TOOL EXECUTION SUCCESS
Observation: Current weather in Vancouver: Temperature: 18°C, Condition: Partly cloudy, Humidity: 65%
```
Shows exactly what tools are being used and their results.

### Memory Management Logs
```
💾 CONVERSATION ADDED TO MEMORY
User: web_user
Short-term Memory Count: 3/10
User Message Length: 34 chars
AI Response Length: 157 chars
```
Shows how conversations are being stored and managed.

## ⚙️ Configuration Options

### Production Settings
For production environments, you may want to reduce logging verbosity:

```python
# In settings.py
AGENT_DEBUG_MODE = False       # Disable debug features
SHOW_AGENT_THOUGHTS = False    # Hide internal thoughts
SHOW_TOOL_EXECUTIONS = True    # Keep tool monitoring
SHOW_OBSERVATIONS = True       # Keep result monitoring
```

### Custom Log Levels
Adjust log levels for different components:

```python
'loggers': {
    'LineBot.agent.react_agent': {
        'level': 'WARNING',  # Only show warnings and errors
    },
    'LineBot.agent.tool_manager': {
        'level': 'INFO',     # Show all tool operations
    },
}
```

## 🐛 Troubleshooting

### Common Issues

#### No Logs Appearing
1. Check that `AGENT_DEBUG_MODE = True` in settings
2. Verify logging configuration is properly loaded
3. Make sure you're running from the correct directory

#### Too Much Log Output
1. Set `SHOW_AGENT_THOUGHTS = False` to reduce verbosity
2. Adjust log levels to 'WARNING' or 'ERROR'
3. Use log filtering tools like `grep`

#### Performance Impact
1. Logging adds minimal overhead in production
2. Disable `SHOW_AGENT_THOUGHTS` for better performance
3. Consider using separate log files instead of console output

### Log File Output
To save logs to files instead of console:

```python
'handlers': {
    'agent_file': {
        'class': 'logging.FileHandler',
        'filename': 'logs/agent.log',
        'formatter': 'agent_formatter',
    },
}
```

## 📈 Monitoring Best Practices

### For Development
- Enable all logging options
- Use the test script regularly
- Monitor tool execution times
- Track memory usage patterns

### For Production
- Log errors and warnings only
- Monitor tool failures
- Track response times
- Set up log rotation

### For Debugging
- Enable maximum verbosity
- Use log timestamps to track performance
- Monitor iteration counts for efficiency
- Check tool success/failure rates

## 🔗 Related Files

- `ChatBot/ChatBot/settings.py` - Logging configuration
- `ChatBot/LineBot/agent/react_agent.py` - Main agent logic
- `ChatBot/LineBot/agent/tool_manager.py` - Tool execution
- `ChatBot/LineBot/agent/output_parser.py` - Response parsing
- `ChatBot/LineBot/agent/memory_manager.py` - Memory operations
- `ChatBot/test_agent_logging.py` - Testing script

## 🤝 Support

If you encounter issues with the logging system:

1. Check the troubleshooting section above
2. Review the test script output for examples
3. Verify your Django configuration
4. Ensure all dependencies are installed

The logging system provides comprehensive insight into how the agent processes information, makes decisions, and interacts with tools. Use this information to optimize agent performance and debug any issues. 