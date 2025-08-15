#!/usr/bin/env python
"""
Expert Evaluation Test Runner with Manual ReAct for o4-mini
Shows explicit thinking process through structured reasoning format
"""
import os
import sys
import django
import json
import time
from datetime import datetime
import random
from openai import OpenAI

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatBot.settings')
django.setup()

from django.conf import settings

class ExpertEvaluationTestRunner:
    def __init__(self):
        """Initialize test runner with OpenAI client"""
        # Check if API key is available
        api_key = settings.OPENAI_API_KEY
        if not api_key or api_key == 'your_openai_api_key_here':
            print("❌ OpenAI API Key not configured!")
            print("Set environment variable: API_KEY=your_actual_key")
            print("Or edit ChatBot/settings.py to set OPENAI_API_KEY directly")
            raise ValueError("OpenAI API key not configured")
        
        self.client = OpenAI(api_key=api_key)
        print(f"✅ OpenAI client initialized successfully")
        
        # Load file search configuration for IoT data access
        self.file_search_config = self.load_file_search_config()
        
        self.results = {
            'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
            'questions': [],
            'gpt_4_1_responses': [],
            'gpt_o4_responses': [],
            'expert_evaluation_pairs': []
        }
        
    def get_expert_evaluation_questions(self):
        """Return all 20 expert evaluation questions - Balanced Questions Using Historical IoT Data + File Search Tests"""
        questions = [
            # DAILY CONVERSATION (4 questions)
            {
                'id': 1,
                'category': 'Daily Conversation',
                'question': "What's the capital of France?"
            },
            {
                'id': 2,
                'category': 'Daily Conversation',
                'question': "What's 25% of 200?"
            },
            {
                'id': 3,
                'category': 'Daily Conversation',
                'question': "Tell me three fruits rich in vitamin C."
            },
            {
                'id': 4,
                'category': 'Daily Conversation',
                'question': "Convert 100 Fahrenheit to Celsius."
            },
            
            # INTENT RECOGNITION (4 questions)
            {
                'id': 5,
                'category': 'Intent Recognition',
                'question': "I'm worried about air quality in my home. Can you help me understand what to look for in environmental data?"
            },
            {
                'id': 6,
                'category': 'Intent Recognition',
                'question': "My allergies are acting up in this room. Could it be related to indoor air quality?"
            },
            {
                'id': 7,
                'category': 'Intent Recognition',
                'question': "Can you help me understand what our environmental data means for my family's health?"
            },
            {
                'id': 8,
                'category': 'Intent Recognition',
                'question': "Something doesn't feel right about the air in this space."
            },
            
            # REASONING TASK (6 questions)
            {
                'id': 9,
                'category': 'Reasoning Task',
                'question': "Using your humidity historical data, calculate the average from any 7-day period and compare to optimal ranges (30-50%)."
            },
            {
                'id': 10,
                'category': 'Reasoning Task',
                'question': "Based on your historical CO2 data, explain what CO2 levels around 820 ppm mean for health and daily activities."
            },
            {
                'id': 11,
                'category': 'Reasoning Task',
                'question': "If your historical data shows humidity at 68% and temperature at 25°C, what might explain allergy symptoms in that environment?"
            },
            {
                'id': 12,
                'category': 'Reasoning Task',
                'question': "From your TVOC historical data, if readings show 300 ppb, how much above the safe limit of 220 ppb would that be?"
            },
            {
                'id': 13,
                'category': 'Reasoning Task',
                'question': "Based on your historical environmental data, evaluate if conditions with CO2: 680 ppm, humidity: 55%, temperature: 23°C would be safe for pregnant women."
            },
            {
                'id': 14,
                'category': 'Reasoning Task',
                'question': "Using your historical data patterns, if someone with asthma enters a room with CO2 at 750 ppm, humidity at 68%, and TVOC at 180 ppb, what should they expect?"
            },
            
            # MULTI-TASK TEST (2 questions)
            {
                'id': 15,
                'category': 'Multi-Task Test',
                'question': "Analyze sample readings from your historical datasets - CO2: 850 ppm, Temperature: 24°C, Humidity: 65%, TVOC: 250 ppb - evaluate each parameter and provide an overall environmental assessment."
            },
            {
                'id': 16,
                'category': 'Multi-Task Test',
                'question': "Using your historical data context, if environmental readings show CO2 at 950 ppm, temperature at 26°C, and humidity at 70%, assess health risks, check safety thresholds, and recommend actions."
            },
            
            # MEMORY TEST (2 questions - 1 pair)
            {
                'id': 17,
                'category': 'Memory Test',
                'question': "From your historical CO2 data, if levels were 720 ppm on a Wednesday, what does that indicate?",
                'memory_context': None
            },
            {
                'id': 18,
                'category': 'Memory Test',
                'question': "Based on that CO2 level you just analyzed, are those conditions safe for children?",
                'memory_context': "Previous question about 720 ppm CO2"
            },
            
            # FILE SEARCH TEST (2 questions to verify file search tool usage)
            {
                'id': 19,
                'category': 'File Search Test',
                'question': "Search your IoT sensor files and tell me the exact CO2 reading from sensor ID 14 on December 16, 2024 at 18:40. Include the file name where you found this data.",
                'memory_context': None
            },
            {
                'id': 20,
                'category': 'File Search Test', 
                'question': "From your historical sensor data files, find the highest TVOC reading recorded and tell me: the exact value, sensor ID, date/time, and which specific file contained this information.",
                'memory_context': None
            }
        ]
        
        return questions
    
    def load_file_search_config(self):
        """Load file search configuration for IoT data access"""
        try:
            with open('file_search_config.json', 'r') as f:
                config = json.load(f)
            
            vector_store_id = config.get('vector_store_id')
            if vector_store_id:
                print(f"📁 File search enabled: {vector_store_id}")
                print(f"   IoT files: {', '.join(config.get('file_names', []))}")
                return config
            else:
                print("⚠️  No vector store found in config")
                return None
                
        except FileNotFoundError:
            print("⚠️  File search config not found (file_search_config.json)")
            print("   Models will work without IoT data access")
            return None
        except Exception as e:
            print(f"⚠️  Could not load file search config: {e}")
            return None
        
    def create_gpt_4_1_prompt(self, question: str, memory_context: str = None) -> list:
        """Create properly engineered prompt for gpt-4.1-mini using developer/user roles"""
        
        # Check if file search is available
        file_search_available = self.file_search_config is not None
        file_search_note = ""
        if file_search_available:
            file_names = ", ".join(self.file_search_config.get('file_names', ['IoT sensor data']))
            file_search_note = f"""

## FILE SEARCH ACCESS 🔍
You have access to historical IoT sensor data files: {file_names}

WHEN TO SEARCH FILES:
* When questions mention specific data, dates, or measurements
* When asked about historical trends or patterns
* When you need actual sensor readings to provide accurate answers
* For questions about CO2, humidity, temperature, or TVOC data

FILE SEARCH PROCESS:
1. ALWAYS indicate when you're searching files: "Let me search the historical data..."
2. Be specific about what you're looking for: "Searching for CO2 readings on Wednesday..."
3. Reference the specific files and data you found: "From iot_co2_data.csv, I found..."
4. Show the actual data points you're using in your analysis

MAKE FILE SEARCH VISIBLE - Users want to see when and how you access their data!"""
        
        # Developer message with structured prompt engineering
        developer_instructions = f"""# Identity

You are an expert IoT environmental monitoring assistant specializing in indoor air quality analysis. You provide accurate, evidence-based insights on temperature, humidity, CO2, and TVOC measurements.{file_search_note}

# Instructions

## Core Capabilities
* Analyze environmental data with scientific accuracy
* Provide health and safety assessments based on established standards
* Calculate mathematical relationships between environmental parameters
* Explain correlations and trends in environmental conditions
* Offer practical recommendations for indoor air quality improvement
* {'🔍 Search through historical IoT sensor data files for relevant measurements' if file_search_available else 'Work with provided data and general knowledge'}

## Response Requirements
* Use specific numerical data when provided
* Reference established safety standards (WHO, EPA, ASHRAE guidelines)
* Show mathematical calculations step-by-step when relevant
* Provide clear explanations with logical reasoning
* Include health implications when assessing environmental conditions
* {'📊 When using file search, clearly indicate: "Searching historical data..." and cite specific files/data found' if file_search_available else 'Work with available information'}

## Safety Standards Reference
* CO2: Optimal <400ppm, Acceptable <1000ppm, Poor >1000ppm
* Temperature: Comfort 20-24°C (68-75°F)
* Humidity: Optimal 30-50%, Acceptable 40-60%
* TVOC: Good <220ppb, Moderate 220-660ppb, Poor >660ppb

## Refusal Protocol
Only refuse when you genuinely don't know the answer or lack the necessary information:
- For requests requiring data you don't have access to
- For highly specialized topics outside your knowledge base
- NOT for basic math, conversions, or general knowledge you clearly possess

When refusing: "I don't have access to [specific information needed]. However, I can help you with [environmental alternative]. [Brief explanation]"

# Examples

<user_query>
What's the average of these CO2 readings: 400, 450, 425, 475 ppm?
</user_query>

<assistant_response>
To calculate the average CO2 levels:
(400 + 450 + 425 + 475) ÷ 4 = 1,750 ÷ 4 = 437.5 ppm

This average of 437.5 ppm is slightly above the optimal range (<400 ppm) but well within acceptable indoor levels (<1000 ppm). This indicates good air quality with minor ventilation improvement opportunities.
</assistant_response>

<user_query>
Should I be concerned about humidity at 65%?
</user_query>

<assistant_response>
Humidity at 65% is above the optimal range (30-50%) and at the upper end of acceptable levels (40-60%). This level may:
- Increase risk of mold growth
- Create discomfort in warmer conditions
- Potentially trigger respiratory issues for sensitive individuals

I recommend improving ventilation or using dehumidification to bring levels closer to 45-50% for optimal comfort and health.
</assistant_response>

<user_query>
Convert 100°F to Celsius.
</user_query>

<assistant_response>
To convert 100°F to Celsius:
°C = (°F - 32) × 5/9
°C = (100 - 32) × 5/9 = 68 × 5/9 ≈ 37.78°C

100°F converts to approximately 37.78°C, which is well above the optimal indoor comfort range of 20-24°C, indicating conditions that would be uncomfortably warm for most indoor environments.
</assistant_response>""" + (f"""

<user_query>
From your historical CO2 data, what were the levels on Wednesday?
</user_query>

<assistant_response>
🔍 Let me search the historical data for Wednesday CO2 readings...

Searching iot_co2_data.csv for Wednesday measurements...

📊 Found CO2 data from iot_co2_data.csv:
- Wednesday, March 13: 720 ppm at 14:30
- Wednesday, March 20: 680 ppm at 15:45
- Wednesday, March 27: 590 ppm at 16:20

Analysis: These Wednesday readings range from 590-720 ppm, which are above optimal (<400 ppm) but below concerning levels (<1000 ppm). The 720 ppm reading suggests a need for improved ventilation during peak afternoon hours.
</assistant_response>""" if file_search_available else "")

        # User message with context if needed
        if memory_context:
            user_message = f"Context: {memory_context}\n\nQuestion: {question}"
        else:
            user_message = question
            
        return [
            {"role": "developer", "content": developer_instructions},
            {"role": "user", "content": user_message}
        ]
    
    def create_o4_react_prompt(self, question: str, memory_context: str = None) -> str:
        """Create manual ReAct prompt for o4-mini-2025-04-16 to show explicit thinking process"""
        
        context_part = f"Previous Context: {memory_context}\n\n" if memory_context else ""
        
        # Check if file search is available for ReAct prompt
        file_search_available = self.file_search_config is not None
        file_search_instructions = ""
        if file_search_available:
            file_names = ", ".join(self.file_search_config.get('file_names', ['IoT sensor data']))
            file_search_instructions = f"""

FILE SEARCH INTEGRATION 🔍:
You have access to historical IoT data: {file_names}
Integrate file search into your ReAct process:

Action: Search historical data for [specific parameters]
Observation: Found [specific data points from files] - cite the exact file and values
Action: Analyze the retrieved data for [patterns/calculations]
Observation: [Analysis results based on found data]

ALWAYS make file searches explicit in your Action steps!"""
        
        react_prompt = f"""You are an expert environmental monitoring assistant with access to historical IoT sensor data. For each question, you MUST reason step-by-step using EXACTLY this format:

Question: [The user's question]
Thought: [Your initial thinking about what needs to be analyzed - consider if you need historical data]
Action: [What specific analysis, calculation, or FILE SEARCH you need to perform]
Observation: [The results of your analysis, including data from files, calculations, or assessments]
Thought: [Further reasoning based on the observations]
Action: [Additional analysis, file search, or moving to conclusion]
Observation: [Additional results if any]
Answer: [Your final comprehensive response with specific recommendations and data citations]

CRITICAL REQUIREMENTS:
- You MUST use the exact format above
- Each section must be clearly labeled
- Show your step-by-step thinking process
- Include specific calculations and data analysis
- Reference environmental safety standards
- Provide actionable insights
- {'🔍 When searching files, be explicit: "Action: Search iot_co2_data.csv for Wednesday readings" and cite specific data found' if file_search_available else 'Work with available information'}{file_search_instructions}

Environmental Standards for Reference:
- CO2: Optimal <400ppm, Acceptable <1000ppm, Poor >1000ppm
- Temperature: Comfort 20-24°C (68-75°F)  
- Humidity: Optimal 30-50%, Acceptable 40-60%
- TVOC: Good <220ppb, Moderate 220-660ppb, Poor >660ppb""" + (f"""

EXAMPLE FILE SEARCH ReAct PROCESS:

Question: What were the CO2 levels on Wednesday?
Thought: I need to find historical CO2 data for Wednesday. I should search the available IoT files for Wednesday measurements.
Action: Search iot_co2_data.csv for Wednesday CO2 readings
Observation: Found 3 Wednesday entries: 720 ppm (Mar 13, 14:30), 680 ppm (Mar 20, 15:45), 590 ppm (Mar 27, 16:20)
Thought: These readings range from 590-720 ppm. I need to analyze these against safety standards and identify any patterns or concerns.
Action: Analyze the Wednesday CO2 trends and assess against optimal (<400ppm) and acceptable (<1000ppm) levels
Observation: All readings exceed optimal levels but remain within acceptable range. The 720 ppm reading is concerning and suggests poor ventilation during afternoon hours.
Answer: Based on historical data from iot_co2_data.csv, Wednesday CO2 levels ranged from 590-720 ppm across different weeks. While within acceptable limits (<1000ppm), all readings exceed optimal levels (<400ppm), with the highest reading of 720 ppm indicating need for improved ventilation, especially during afternoon hours (14:30-16:20 timeframe).

MAKE YOUR FILE SEARCHES VISIBLE LIKE THIS EXAMPLE!""" if file_search_available else "") + f"""

Let's begin:

{context_part}Question: {question}
"""
        
        return react_prompt
    
    def call_gpt_4_1_mini(self, messages: list) -> str:
        """Call gpt-4.1-mini using Responses API with file search for IoT data access"""
        try:
            # Convert messages to input format for Responses API
            input_content = "\n\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in messages])
            
            # Prepare tools - add file search if available
            tools = []
            if self.file_search_config and self.file_search_config.get('vector_store_id'):
                tools.append({
                    "type": "file_search",
                    "vector_store_ids": [self.file_search_config['vector_store_id']],
                    "max_num_results": 5
                })
                print(f"      🔧 Adding file_search tool (vector_store: {self.file_search_config['vector_store_id'][:20]}...)")
            
            # Use Responses API
            response = self.client.responses.create(
                model="gpt-4.1-mini-2025-04-14",
                input=input_content,
                tools=tools if tools else None,
                max_output_tokens=800,
                temperature=0.2
            )
            
            # FIXED: Robust response parsing with proper type checking
            text_outputs = []
            
            # Handle direct output_text attribute
            if hasattr(response, 'output_text') and response.output_text:
                return response.output_text
            
            # Handle output array
            if hasattr(response, 'output') and response.output:
                for item in response.output:
                    try:
                        # Method 1: Object format with attributes
                        if hasattr(item, 'type') and item.type == 'message':
                            if hasattr(item, 'content') and item.content:
                                for content_item in item.content:
                                    if hasattr(content_item, 'type') and content_item.type == 'output_text':
                                        if hasattr(content_item, 'text'):
                                            text_outputs.append(content_item.text)
                        
                        # Method 2: Dictionary format
                        elif isinstance(item, dict):
                            if item.get('type') == 'message' and 'content' in item:
                                content_list = item['content']
                                if isinstance(content_list, list):
                                    for content_item in content_list:
                                        # FIXED: Only process dictionaries here
                                        if isinstance(content_item, dict) and content_item.get('type') == 'output_text':
                                            text_outputs.append(content_item.get('text', ''))
                                        # REMOVED: The problematic string handling that caused the error
                                elif isinstance(content_list, str):
                                    # Handle case where content is directly a string
                                    text_outputs.append(content_list)
                        
                        # Method 3: Direct string (fallback)
                        elif isinstance(item, str):
                            text_outputs.append(item)
                            
                    except AttributeError as attr_error:
                        # Log attribute errors for debugging
                        print(f"      ⚠️  Attribute error processing item: {attr_error}")
                        continue
                    except Exception as parse_error:
                        # Log other parsing errors
                        print(f"      ⚠️  Parsing error for item: {parse_error}")
                        continue
            
            # Return combined text or error message
            if text_outputs:
                return '\n'.join(text_outputs)
            else:
                # Enhanced debugging without causing new errors
                try:
                    debug_info = []
                    for i, item in enumerate(response.output[:3]):  # Limit to first 3 items
                        item_type = type(item).__name__
                        if hasattr(item, 'type'):
                            debug_info.append(f"Item{i}:{item_type}(type={item.type})")
                        elif isinstance(item, dict):
                            debug_info.append(f"Item{i}:dict(keys={list(item.keys())[:3]})")
                        else:
                            debug_info.append(f"Item{i}:{item_type}")
                    
                    return f"ERROR: No text extracted from gpt-4.1-mini. Debug: {'; '.join(debug_info)}"
                except:
                    return "ERROR: Failed to parse gpt-4.1-mini response and debug info unavailable"
            
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def call_gpt_o4_mini_react(self, react_prompt: str) -> str:
        """Call o4-mini-2025-04-16 following official OpenAI documentation pattern"""
        try:
            # Prepare tools - add file search if available
            tools = []
            if self.file_search_config and self.file_search_config.get('vector_store_id'):
                tools.append({
                    "type": "file_search",
                    "vector_store_ids": [self.file_search_config['vector_store_id']],
                    "max_num_results": 5
                })
                print(f"      🔧 Adding file_search tool with ReAct (vector_store: {self.file_search_config['vector_store_id'][:20]}...)")
            
            # Use Responses API exactly as shown in OpenAI docs
            response = self.client.responses.create(
                model="o4-mini-2025-04-16",
                reasoning={"effort": "medium"},
                input=[
                    {
                        "role": "user",
                        "content": react_prompt
                    }
                ],
                tools=tools if tools else None,
                max_output_tokens=25000  # OpenAI recommends at least 25,000 tokens for reasoning models
            )
            
            # OFFICIAL PATTERN: Check response.output_text first (as per OpenAI docs)
            if hasattr(response, 'output_text') and response.output_text:
                return response.output_text
            
            # Handle incomplete responses (as shown in OpenAI docs)
            if hasattr(response, 'status') and response.status == "incomplete":
                if hasattr(response, 'incomplete_details') and response.incomplete_details:
                    reason = response.incomplete_details.reason if hasattr(response.incomplete_details, 'reason') else 'unknown'
                    if reason == "max_output_tokens":
                        # Check if we got partial output
                        if hasattr(response, 'output_text') and response.output_text:
                            return f"INCOMPLETE: Ran out of tokens during reasoning. Partial output: {response.output_text}"
                        else:
                            return "ERROR: Ran out of tokens during reasoning phase before generating visible output"
                    else:
                        return f"ERROR: Incomplete response - {reason}"
                else:
                    return "ERROR: Response marked as incomplete but no details available"
            
            # OFFICIAL PATTERN: Parse output array following OpenAI documentation
            if hasattr(response, 'output') and response.output:
                text_outputs = []
                file_search_calls = 0
                reasoning_steps = 0
                
                for item in response.output:
                    try:
                        # Log what we're processing (for debugging)
                        item_type = getattr(item, 'type', None) or (item.get('type') if isinstance(item, dict) else 'unknown')
                        
                        # Count different item types
                        if item_type == 'file_search_call':
                            file_search_calls += 1
                        elif item_type == 'reasoning':
                            reasoning_steps += 1
                        
                        # METHOD 1: Handle object format (hasattr access)
                        if hasattr(item, 'type'):
                            # Look for message items (these contain the final text)
                            if item.type == 'message':
                                if hasattr(item, 'content') and item.content:
                                    # Process content array
                                    for content_item in item.content:
                                        if hasattr(content_item, 'type') and content_item.type == 'output_text':
                                            if hasattr(content_item, 'text') and content_item.text:
                                                text_outputs.append(content_item.text)
                            
                            # Skip reasoning items (internal, encrypted)
                            elif item.type == 'reasoning':
                                continue
                            
                            # Skip tool calls (intermediate steps)
                            elif item.type in ['file_search_call', 'tool_call']:
                                continue
                        
                        # METHOD 2: Handle dictionary format
                        elif isinstance(item, dict):
                            if item.get('type') == 'message':
                                content_list = item.get('content', [])
                                if isinstance(content_list, list):
                                    for content_item in content_list:
                                        if isinstance(content_item, dict):
                                            if content_item.get('type') == 'output_text':
                                                text_content = content_item.get('text', '')
                                                if text_content:
                                                    text_outputs.append(text_content)
                            
                            # Skip reasoning and tool calls
                            elif item.get('type') in ['reasoning', 'file_search_call', 'tool_call']:
                                continue
                        
                        # METHOD 3: Direct string content (rare but possible)
                        elif isinstance(item, str):
                            text_outputs.append(item)
                            
                    except Exception as parse_error:
                        print(f"      ⚠️  Error parsing {item_type} item: {parse_error}")
                        continue
                
                # Debug info for troubleshooting
                print(f"      📊 Found: {reasoning_steps} reasoning steps, {file_search_calls} file searches, {len(text_outputs)} text outputs")
                
                if text_outputs:
                    return '\n'.join(text_outputs)
            
            # DEBUG: Provide detailed analysis of what we received
            debug_items = []
            reasoning_count = 0
            tool_call_count = 0
            
            if hasattr(response, 'output') and response.output:
                for item in response.output[:5]:  # Check first 5 items
                    if hasattr(item, 'type'):
                        item_type = item.type
                        if item_type == 'reasoning':
                            reasoning_count += 1
                        elif item_type in ['file_search_call', 'tool_call']:
                            tool_call_count += 1
                        debug_items.append(item_type)
                    elif isinstance(item, dict):
                        debug_items.append(f"dict({item.get('type', 'no_type')})")
                    else:
                        debug_items.append(type(item).__name__)
            
            # Provide specific guidance for reasoning models
            if reasoning_count > 0 and tool_call_count > 0:
                return f"ERROR: o4-mini generated {reasoning_count} reasoning steps and {tool_call_count} tool calls, but no final text output. The model may be hitting token limits during reasoning. Items: {', '.join(debug_items)}"
            elif reasoning_count > 0:
                return f"ERROR: o4-mini generated {reasoning_count} reasoning steps but no final output. May need higher max_output_tokens. Items: {', '.join(debug_items)}"
            else:
                return f"ERROR: Unexpected o4-mini response format. No output_text found. Items: {', '.join(debug_items)}"
            
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def run_single_model_test(self, model_name: str, questions: list) -> list:
        """Run all questions on a single model"""
        print(f"\n🤖 Testing {model_name}")
        print("=" * 50)
        
        responses = []
        
        for i, q in enumerate(questions, 1):
            print(f"Question {i}/{len(questions)}: {q['category']}")
            
            try:
                start_time = time.time()
                
                # Handle memory context for sequential questions
                memory_context = None
                if q.get('memory_context'):
                    if q['id'] == 18:  # Follows question 17
                        memory_context = "You previously discussed CO2 levels of 720 ppm on Wednesday."
                
                # Create appropriate prompts and calls for each model
                if model_name == "gpt-4.1-mini":
                    # Show file search status
                    if self.file_search_config:
                        print(f"  🔍 File search enabled: {len(self.file_search_config.get('file_ids', []))} IoT files available")
                    else:
                        print(f"  📭 File search disabled: No IoT data access")
                    
                    messages = self.create_gpt_4_1_prompt(q['question'], memory_context)
                    response = self.call_gpt_4_1_mini(messages)
                    prompt_data = messages
                elif model_name == "gpt-o4-mini-react":  # gpt-o4-mini-2025-04-16 with manual ReAct
                    # Show file search status 
                    if self.file_search_config:
                        print(f"  🔍 File search + ReAct enabled: Visible reasoning with IoT data access")
                    else:
                        print(f"  📭 ReAct only: No IoT data access")
                    
                    react_prompt = self.create_o4_react_prompt(q['question'], memory_context)
                    response = self.call_gpt_o4_mini_react(react_prompt)
                    prompt_data = react_prompt
                else:
                    raise ValueError(f"Unknown model name: {model_name}. Expected 'gpt-4.1-mini' or 'gpt-o4-mini-react'")
                
                processing_time = time.time() - start_time
                
                response_data = {
                    'question_id': q['id'],
                    'category': q['category'],
                    'question': q['question'],
                    'response': response,
                    'processing_time': processing_time,
                    'memory_context': memory_context,
                    'prompt_data': prompt_data
                }
                
                responses.append(response_data)
                
                print(f"  ✅ Completed in {processing_time:.2f}s")
                
                # Brief pause between questions
                time.sleep(1)
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                responses.append({
                    'question_id': q['id'],
                    'category': q['category'], 
                    'question': q['question'],
                    'response': f"ERROR: {str(e)}",
                    'processing_time': 0,
                    'memory_context': memory_context,
                    'prompt_data': f"ERROR - Failed to generate prompt for {model_name}"
                })
        
        return responses
    
    def create_expert_evaluation_pairs(self, gpt_4_1_responses: list, gpt_o4_responses: list) -> list:
        """Create randomized response pairs for expert evaluation"""
        evaluation_pairs = []
        
        for i in range(len(gpt_4_1_responses)):
            # Randomize which response is A and which is B
            if random.choice([True, False]):
                model_a = 'gpt-4.1-mini'
                model_b = 'gpt-o4-mini-react'
                response_a = gpt_4_1_responses[i]['response']
                response_b = gpt_o4_responses[i]['response']
            else:
                model_a = 'gpt-o4-mini-react'
                model_b = 'gpt-4.1-mini'
                response_a = gpt_o4_responses[i]['response']
                response_b = gpt_4_1_responses[i]['response']
            
            pair = {
                'question_id': gpt_4_1_responses[i]['question_id'],
                'category': gpt_4_1_responses[i]['category'],
                'question': gpt_4_1_responses[i]['question'],
                'memory_context': gpt_4_1_responses[i].get('memory_context'),
                'response_a': response_a,
                'response_b': response_b,
                'model_a': model_a,
                'model_b': model_b,
                'randomization_seed': random.randint(1000, 9999)
            }
            
            evaluation_pairs.append(pair)
        
        return evaluation_pairs
    
    def save_results(self, gpt_4_1_responses: list, gpt_o4_responses: list, evaluation_pairs: list) -> tuple:
        """Save all results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Complete results file
        complete_results = {
            'timestamp': timestamp,
            'total_questions': len(gpt_4_1_responses),
            'methodology': 'Direct OpenAI API calls with model-specific prompt engineering',
            'model_versions': {
                'gpt_4_1_mini': 'gpt-4.1-mini-2025-04-14',
                'o4_mini': 'o4-mini-2025-04-16'
            },
            'api_usage': {
                'gpt_4_1_mini': 'Chat Completions API with structured developer/user prompts',
                'o4_mini': 'Responses API with manual ReAct format for visible reasoning'
            },
            'prompt_engineering': {
                'gpt_4_1_mini': 'GPT model: Detailed instructions with identity, examples, safety standards',
                'o4_mini': 'Reasoning model: Manual ReAct structure (Question→Thought→Action→Observation→Answer) to show explicit thinking process'
            },
            'reasoning_approach': {
                'gpt_4_1_mini': 'Standard structured prompting',
                'o4_mini': 'Manual ReAct implementation with step-by-step visible reasoning'
            },
            'pricing_info': {
                'gpt_4_1_mini': {'input': '$0.40/1M', 'cached_input': '$0.10/1M', 'output': '$1.60/1M'},
                'o4_mini': {'input': '$1.10/1M', 'cached_input': '$0.275/1M', 'output': '$4.40/1M'}
            },
            'gpt_4_1_mini_responses': gpt_4_1_responses,
            'gpt_o4_mini_react_responses': gpt_o4_responses,
            'expert_evaluation_pairs': evaluation_pairs
        }
        
        # Save complete results
        results_file = f"expert_evaluation_complete_{timestamp}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(complete_results, f, indent=2, ensure_ascii=False)
        
        # Save expert evaluation file (clean format for experts)
        expert_file = f"expert_evaluation_form_{timestamp}.json"
        expert_format = {
            'instructions': 'Evaluate each response pair. Model B uses explicit ReAct reasoning (shows Thought→Action→Observation steps)',
            'evaluation_criteria': {
                'task_completion': 'Which response better addresses all parts of the question?',
                'reasoning_quality': 'Which response shows better analytical thinking? (Note: One shows explicit step-by-step reasoning)',
                'accuracy_relevance': 'Which response is more accurate and relevant to environmental monitoring?',
                'usefulness': 'Which response would be more helpful to a user seeking air quality guidance?',
                'transparency': 'Which response makes the reasoning process more clear and understandable?',
                'overall_preference': 'Overall, which response is better?'
            },
            'scale': {
                '+2': 'A is much better',
                '+1': 'A is better', 
                '0': 'Equal/Tie',
                '-1': 'B is better',
                '-2': 'B is much better'
            },
            'note': 'One model uses manual ReAct format showing explicit reasoning steps',
            'evaluation_pairs': evaluation_pairs
        }
        
        with open(expert_file, 'w', encoding='utf-8') as f:
            json.dump(expert_format, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved:")
        print(f"   Complete results: {results_file}")
        print(f"   Expert evaluation: {expert_file}")
        
        return results_file, expert_file
    
    def generate_summary_report(self, gpt_4_1_responses: list, gpt_o4_responses: list):
        """Generate summary report of responses"""
        print(f"\n📊 SUMMARY REPORT")
        print("=" * 50)
        
        # Response length analysis
        gpt_4_1_lengths = [len(r['response']) for r in gpt_4_1_responses if not r['response'].startswith('ERROR')]
        gpt_o4_lengths = [len(r['response']) for r in gpt_o4_responses if not r['response'].startswith('ERROR')]
        
        print(f"gpt-4.1-mini-2025-04-14 (Chat Completions + developer/user prompts):")
        if gpt_4_1_lengths:  # Prevent division by zero
            print(f"  Average response length: {sum(gpt_4_1_lengths)/len(gpt_4_1_lengths):.0f} characters")
        else:
            print(f"  Average response length: N/A (all responses had errors)")
        print(f"  Error count: {sum(1 for r in gpt_4_1_responses if r['response'].startswith('ERROR'))}")
        print(f"  Cost: $0.40 input / $1.60 output per 1M tokens (max 300 tokens/response)")
        
        print(f"o4-mini-2025-04-16 (Responses API + Manual ReAct reasoning):")
        if gpt_o4_lengths:  # Prevent division by zero
            print(f"  Average response length: {sum(gpt_o4_lengths)/len(gpt_o4_lengths):.0f} characters")
        else:
            print(f"  Average response length: N/A (all responses had errors)")
        print(f"  Error count: {sum(1 for r in gpt_o4_responses if r['response'].startswith('ERROR'))}")
        print(f"  Cost: $1.10 input / $4.40 output per 1M tokens (max 1200 tokens/response)")
        print(f"  Format: Explicit Question→Thought→Action→Observation→Answer structure")
        
        # Category breakdown
        categories = set(r['category'] for r in gpt_4_1_responses)
        print(f"\nCategory distribution:")
        for category in categories:
            count = sum(1 for r in gpt_4_1_responses if r['category'] == category)
            print(f"  {category}: {count} questions")
        
        print(f"\nTotal questions: {len(gpt_4_1_responses)}")
        print(f"Key Difference:")
        print(f"  • gpt-4.1-mini: Standard structured prompting")
        print(f"  • o4-mini-2025-04-16: Manual ReAct with VISIBLE step-by-step reasoning")
    
    def run_complete_evaluation(self):
        """Run complete evaluation on both models"""
        print("🎓 EXPERT EVALUATION TEST RUNNER")
        print("=" * 50)
        print("Balanced Questions Using Historical IoT Data:")
        print("• 20 questions across 6 categories: Daily Conversation, Intent Recognition,")
        print("  Reasoning Task, Multi-Task Test, Memory Test, File Search Test")
        print("• gpt-4.1-mini-2025-04-14: Chat Completions + Structured prompts")
        print("• o4-mini-2025-04-16: Responses API + Manual ReAct (VISIBLE reasoning)")
        
        # Get questions
        questions = self.get_expert_evaluation_questions()
        self.results['questions'] = questions
        
        # Test gpt-4.1-mini with Chat Completions API
        print("\n" + "="*75)
        print("TESTING gpt-4.1-mini-2025-04-14 via Chat Completions API")
        print("• Structured Developer/User prompts with detailed instructions")
        print("• Cost: $0.40 input / $1.60 output per 1M tokens (max 300 tokens/response)")
        print("="*75)
        gpt_4_1_responses = self.run_single_model_test("gpt-4.1-mini", questions)
        
        # Test o4-mini-2025-04-16 with Manual ReAct
        print("\n" + "="*75)
        print("TESTING o4-mini-2025-04-16 with Manual ReAct Structure")
        print("• Question→Thought→Action→Observation→Answer format")
        print("• VISIBLE step-by-step reasoning process")
        print("• Cost: $1.10 input / $4.40 output per 1M tokens (max 1200 tokens/response)")
        print("="*75)
        gpt_o4_responses = self.run_single_model_test("gpt-o4-mini-react", questions)
        
        # Create evaluation pairs
        print("\n🔀 Creating randomized evaluation pairs...")
        evaluation_pairs = self.create_expert_evaluation_pairs(gpt_4_1_responses, gpt_o4_responses)
        
        # Save results
        print("\n💾 Saving results...")
        results_file, expert_file = self.save_results(gpt_4_1_responses, gpt_o4_responses, evaluation_pairs)
        
        # Generate summary
        self.generate_summary_report(gpt_4_1_responses, gpt_o4_responses)
        
        print(f"\n🎯 NEXT STEPS:")
        print(f"1. Send '{expert_file}' to 3-4 expert evaluators")
        print(f"2. Note: One model shows explicit ReAct reasoning steps")
        print(f"3. Evaluate transparency and reasoning quality differences")
        print(f"4. Use complete results in '{results_file}' for analysis")
        
        return results_file, expert_file

def main():
    """Main function to run expert evaluation tests"""
    try:
        runner = ExpertEvaluationTestRunner()
        results_file, expert_file = runner.run_complete_evaluation()
        
        print(f"\n✅ SUCCESS: Expert evaluation data ready!")
        print(f"📁 Files created:")
        print(f"   {results_file}")
        print(f"   {expert_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)