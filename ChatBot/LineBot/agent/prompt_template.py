from datetime import datetime
import pytz

class PromptTemplate:
    
    @staticmethod
    def get_complex_prompt(user_input, tools_description, chat_history=""):
        """Generate prompt for complex LLM"""
        vancouver_tz = pytz.timezone('America/Vancouver')
        current_time = datetime.now(vancouver_tz).strftime("%Y-%m-%d %H:%M:%S PST/PDT")
        
        template = f"""Category Content
background
Current Time: {current_time}
Current Location: Vancouver, Canada

role
You are a helpful AI assistant. Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

tool description
You have access to the following tools:
{tools_description}

format constraints
You MUST use the following format to respond:
Thought: Describe the problem you need to solve next, and think about whether you need to use tools.
If you think you can respond directly to the user without using a tool, please reply:
Final Answer: string \\ Put your final response here.
If you think you need to use a tool, please reply:
Action: A JSON object that contains the tool's name and the tool's inputs.
Observation: the result of action
Thought: a new round of thinking
...
Thought/Action/Observation can repeat several times until you think you no longer need any tool. At this point, please reply:
Thought: I now know the final answer.
Final Answer: string \\ Put your final response here.
If you do not reply in this format, you may cause a programming error.

chat history
The chat history between the user and the AI:
{chat_history if chat_history else "No previous conversation"}

new input
The user's new input:
Human: {user_input}
"""
        
        return template
    
    @staticmethod
    def get_lightweight_prompt(thought, tools_description):
        """Generate prompt for lightweight LLM"""
        vancouver_tz = pytz.timezone('America/Vancouver')
        current_time = datetime.now(vancouver_tz).strftime("%Y-%m-%d %H:%M:%S PST/PDT")

        template = f"""Category Content
background
Current Time: {current_time}
Current Location: Vancouver, Canada

role
You are a helpful AI programmer. You're good at converting the input to JSON.

tool description
You have access to the following tools:
{tools_description}

format constraints
You MUST use the following format to respond:
```json
{{
"action": string, \\ The name of the tool to be used.
"action_inputs": list \\ The inputs for the tool, represented as a list. For boolean values, use true and
false instead of True and False.
}}
```
Only one JSON should be included in your response. If you do not reply in this format, you may cause a programming error.

Thought: {thought}
"""
        
        return template