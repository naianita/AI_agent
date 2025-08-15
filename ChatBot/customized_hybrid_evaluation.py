#!/usr/bin/env python
"""
Customized Hybrid Evaluation System
- Manual evaluation: Questions 9, 15-20 (7 questions)
- Automated evaluation: Questions 1-8, 10-14 (13 questions)
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
from enum import Enum
from openai import OpenAI
from pydantic import BaseModel, Field

# No .env file loading needed - using PowerShell environment variable

class CustomizedHybridEvaluator:
    """Customized evaluator for specific question IDs"""
    
    def __init__(self):
        # Use PowerShell environment variable: $env:API_KEY="sk-..."
        api_key = os.getenv('API_KEY')  # Changed from 'OPENAI_API_KEY' to 'API_KEY'
        if not api_key:
            print("❌ API_KEY environment variable not set!")
            print("In PowerShell, run: $env:API_KEY=\"sk-your_actual_key_here\"")
            raise ValueError("API_KEY environment variable not configured")
        
        self.client = OpenAI(api_key=api_key)
        
        # Define which questions to evaluate manually
        self.manual_question_ids = {9, 17, 18, 19, 20}  # Moved 15, 16 to automated
        
    def classify_questions(self, expert_data: Dict) -> tuple:
        """Classify questions into automated vs manual based on question IDs"""
        
        automated_items = []
        manual_items = []
        
        for pair in expert_data['evaluation_pairs']:
            question_id = pair['question_id']
            
            if question_id in self.manual_question_ids:
                manual_items.append(pair)
            else:
                automated_items.append(pair)
        
        return automated_items, manual_items
    
    def create_automated_evaluation(self, automated_items: List[Dict]):
        """Create Evals API evaluation for automated questions (1-8, 10-16)"""
        
        print(f"🔧 Creating automated evaluation for questions: {[item['question_id'] for item in automated_items]}")
        
        try:
            eval_config = self.client.evals.create(
                name="Fair Model Comparison - Questions 1-8, 10-16",
                data_source_config={
                    "type": "custom",
                    "item_schema": {
                        "type": "object",
                        "properties": {
                            "question_id": {"type": "integer"},
                            "question": {"type": "string"},
                            "category": {"type": "string"},
                            "gpt_response": {"type": "string"},
                            "reasoning_response": {"type": "string"},
                            "task_complexity": {"type": "string"}
                        },
                        "required": ["question_id", "question", "category", "gpt_response", "reasoning_response"]
                    },
                    "include_sample_schema": True
                },
                testing_criteria=[
                    {
                        "type": "llm_grader",
                        "name": "Fair Accuracy Assessment",
                        "instruction": """
Rate accuracy (1-10) for both responses considering model design differences:

CRITICAL FAIR EVALUATION PRINCIPLES:
- GPT models: Expected to give direct, concise answers
- Reasoning models: Expected to show step-by-step thinking process
- Reasoning model's visible thought process is a FEATURE, not verbosity
- Different response styles serve different user needs

Scoring Guidelines:
- Don't penalize reasoning models for showing work
- Don't penalize GPT models for being concise
- Focus on correctness of final answers
- Consider appropriateness for model type

Format: {"gpt_accuracy": X, "reasoning_accuracy": Y, "explanation": "..."}
                        """,
                        "input": "Question: {{ item.question }}\nCategory: {{ item.category }}\nGPT Response: {{ item.gpt_response }}\nReasoning Response: {{ item.reasoning_response }}"
                    },
                    {
                        "type": "llm_grader",
                        "name": "Task Appropriateness (Design-Aware)",
                        "instruction": """
Rate task fit (1-10) based on OpenAI's official model guidance:

MODEL DESIGN EXPECTATIONS:
- Simple tasks (Daily Conversation): Both models should perform well
- Complex tasks (Intent Recognition, Reasoning Tasks): Reasoning models may have advantage
- Multi-step problems: Reasoning models designed to excel here

FAIR SCORING:
- Score based on how well each model performs within its design strengths
- Reasoning models showing explicit steps on complex tasks = HIGH score
- GPT models providing direct answers efficiently = HIGH score
- No bias toward brevity or verbosity - focus on task completion

Format: {"gpt_task_fit": X, "reasoning_task_fit": Y, "complexity": "simple/complex", "explanation": "..."}
                        """,
                        "input": "Category: {{ item.category }}\nQuestion: {{ item.question }}\nGPT Response: {{ item.gpt_response }}\nReasoning Response: {{ item.reasoning_response }}"
                    },
                    {
                        "type": "llm_grader",
                        "name": "User Value Assessment", 
                        "instruction": """
Rate overall user value (1-10) considering different user preferences:

USER PERSPECTIVE CONSIDERATIONS:
- Some users prefer quick, direct answers (GPT strength)
- Some users prefer seeing the thinking process (Reasoning strength)
- Some users want transparency in complex decisions (Reasoning advantage)
- Some users want efficiency in simple tasks (GPT advantage)

EVALUATION CRITERIA:
- Helpfulness: Does the response solve the user's problem?
- Appropriateness: Is the response style suitable for the question type?
- Completeness: Are all aspects of the question addressed?
- Clarity: Is the response easy to understand and use?

Format: {"gpt_user_value": X, "reasoning_user_value": Y, "explanation": "..."}
                        """,
                        "input": "Question: {{ item.question }}\nGPT Response: {{ item.gpt_response }}\nReasoning Response: {{ item.reasoning_response }}"
                    }
                ]
            )
            
            self.automated_eval_id = eval_config.id
            print(f"✅ Automated evaluation created: {self.automated_eval_id}")
            return eval_config
            
        except Exception as e:
            print(f"❌ Error creating automated evaluation: {e}")
            return None
    
    def prepare_automated_data(self, automated_items: List[Dict]) -> str:
        """Prepare data file for automated evaluation"""
        
        eval_data = []
        for pair in automated_items:
            # Determine which response is from which model
            if pair['model_a'] == 'gpt-4.1-mini':
                gpt_response = pair['response_a']
                reasoning_response = pair['response_b']
            else:
                gpt_response = pair['response_b']
                reasoning_response = pair['response_a']
            
            # Classify task complexity
            task_complexity = self.classify_task_complexity(pair['category'], pair['question'])
            
            eval_item = {
                "item": {
                    "question_id": pair['question_id'],
                    "question": pair['question'],
                    "category": pair['category'],
                    "gpt_response": gpt_response,
                    "reasoning_response": reasoning_response,
                    "task_complexity": task_complexity
                }
            }
            eval_data.append(eval_item)
        
        # Save as JSONL
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        eval_file = f"automated_evaluation_questions_1-8_10-16_{timestamp}.jsonl"
        
        with open(eval_file, 'w', encoding='utf-8') as f:
            for item in eval_data:
                f.write(json.dumps(item) + '\n')
        
        # Upload to OpenAI
        print(f"📤 Uploading automated evaluation data...")
        file_response = self.client.files.create(
            file=open(eval_file, 'rb'),
            purpose="evals"
        )
        
        print(f"✅ Automated data uploaded: {file_response.id}")
        return file_response.id
    
    def classify_task_complexity(self, category: str, question: str) -> str:
        """Classify task complexity for fair evaluation"""
        
        simple_categories = ["Daily Conversation"]
        complex_categories = ["Intent Recognition", "Reasoning Task", "Multi-Task Test", "Memory Test"]
        
        if category in simple_categories:
            return "simple"
        elif category in complex_categories:
            return "complex"
        else:
            # Analyze question content
            complex_indicators = ["calculate", "analyze", "compare", "evaluate", "assess", "explain"]
            if any(indicator in question.lower() for indicator in complex_indicators):
                return "complex"
            return "simple"
    
    def generate_manual_evaluation_form(self, manual_items: List[Dict]) -> str:
        """Generate structured manual evaluation form for questions 9, 17-20"""
        
        print(f"📝 Generating manual evaluation form for questions: {[item['question_id'] for item in manual_items]}")
        
        # Create comprehensive manual evaluation structure
        manual_form = {
            "evaluation_info": {
                "type": "Manual Evaluation - Questions 9, 15-20",
                "purpose": "Fair evaluation of complex reasoning and file search tasks",
                "evaluator_instructions": [
                    "These questions require domain expertise or data verification",
                    "Question 9: Requires checking actual humidity data calculations", 
                    "Questions 17-18: Memory test requiring context understanding",
                    "Questions 19-20: File search requiring data verification"
                ],
                "fair_evaluation_principles": {
                    "model_design_awareness": "Reasoning models show explicit thinking - this is valuable, not verbose",
                    "task_appropriateness": "Complex tasks should favor reasoning models (this is their design strength)",
                    "transparency_value": "Visible reasoning process provides educational and verification value",
                    "no_length_bias": "Don't penalize models for their intended design characteristics"
                }
            },
            "scoring_scale": {
                "1-3": "Poor - Major issues or incorrect information",
                "4-6": "Average - Adequate but with room for improvement", 
                "7-8": "Good - High quality response appropriate for model type",
                "9-10": "Excellent - Outstanding performance showcasing model strengths"
            },
            "evaluation_items": []
        }
        
        # Process each manual evaluation item
        for pair in manual_items:
            # Determine which response is from which model
            if pair['model_a'] == 'gpt-4.1-mini':
                gpt_response = pair['response_a']
                reasoning_response = pair['response_b']
            else:
                gpt_response = pair['response_b']
                reasoning_response = pair['response_a']
            
            # Create detailed evaluation structure for each question
            eval_item = {
                "question_id": pair['question_id'],
                "category": pair['category'],
                "question": pair['question'],
                "context": self.get_question_context(pair['question_id']),
                "responses": {
                    "gpt_4_1_mini": {
                        "text": gpt_response,
                        "expected_characteristics": "Direct, concise answer with environmental expertise"
                    },
                    "o4_mini_reasoning": {
                        "text": reasoning_response,
                        "expected_characteristics": "Step-by-step reasoning process showing explicit thinking"
                    }
                },
                "evaluation_dimensions": {
                    "accuracy": {
                        "description": "Correctness of information and calculations",
                        "gpt_score": None,
                        "reasoning_score": None,
                        "notes": ""
                    },
                    "completeness": {
                        "description": "How thoroughly the question is addressed",
                        "gpt_score": None,
                        "reasoning_score": None,
                        "notes": ""
                    },
                    "task_appropriateness": {
                        "description": "How well response matches model's design strengths",
                        "gpt_score": None,
                        "reasoning_score": None,
                        "notes": "Consider: complex tasks should favor reasoning models"
                    },
                    "transparency": {
                        "description": "Clarity of reasoning and process visibility",
                        "gpt_score": None,
                        "reasoning_score": None,
                        "notes": "Reasoning model's visible process is a feature, not verbosity"
                    },
                    "practical_value": {
                        "description": "Real-world usefulness to users",
                        "gpt_score": None,
                        "reasoning_score": None,
                        "notes": ""
                    }
                },
                "overall_assessment": {
                    "preferred_model": None,  # "gpt-4.1-mini", "o4-mini", or "tie"
                    "confidence": None,       # 1-10
                    "reasoning": "",
                    "bias_check": ""          # Note any evaluation biases to avoid
                }
            }
            
            manual_form["evaluation_items"].append(eval_item)
        
        # Save manual evaluation form
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        manual_file = f"manual_evaluation_questions_9_17-20_{timestamp}.json"
        
        with open(manual_file, 'w', encoding='utf-8') as f:
            json.dump(manual_form, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Manual evaluation form saved: {manual_file}")
        return manual_file
    
    def get_question_context(self, question_id: int) -> str:
        """Provide context for specific questions requiring manual evaluation"""
        
        contexts = {
            9: "Data calculation task - requires verifying actual humidity data and mathematical accuracy",
            17: "Memory test baseline - establishes context for question 18",
            18: "Memory test follow-up - requires understanding context from question 17",
            19: "File search accuracy test - requires verification against actual IoT data files",
            20: "File search comprehensive test - requires finding maximum values in actual data"
        }
        
        return contexts.get(question_id, "Manual evaluation required for this question type")
    
    def run_customized_evaluation(self, expert_file: str):
        """Run the customized hybrid evaluation"""
        
        print("🚀 Customized Hybrid Fair Evaluation System")
        print("Manual: Questions 9, 17-20 | Automated: Questions 1-8, 10-16")
        print("=" * 65)
        
        # Load expert data
        with open(expert_file, 'r', encoding='utf-8') as f:
            expert_data = json.load(f)
        
        # Classify questions
        automated_items, manual_items = self.classify_questions(expert_data)
        
        # Sort for clarity
        automated_items.sort(key=lambda x: x['question_id'])
        manual_items.sort(key=lambda x: x['question_id'])
        
        print(f"📊 Question Classification:")
        print(f"  🤖 Automated: {[item['question_id'] for item in automated_items]} ({len(automated_items)} questions)")
        print(f"  👤 Manual: {[item['question_id'] for item in manual_items]} ({len(manual_items)} questions)")
        
        # Run automated evaluation
        automated_results = None
        if automated_items:
            eval_config = self.create_automated_evaluation(automated_items)
            if eval_config:
                data_file_id = self.prepare_automated_data(automated_items)
                
                print(f"🔄 Starting automated evaluation...")
                try:
                    run_response = self.client.evals.runs.create(
                        self.automated_eval_id,
                        name=f"Fair Comparison Q1-8,10-16 - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        data_source={
                            "type": "completions",
                            "model": "gpt-4o-2024-08-06",
                            "source": {"type": "file_id", "id": data_file_id}
                        }
                    )
                    
                    print(f"✅ Automated evaluation running: {run_response.id}")
                    print(f"📊 Dashboard: {run_response.report_url}")
                    
                    # Save the IDs for later use
                    automation_info = {
                        "eval_id": self.automated_eval_id,
                        "run_id": run_response.id,
                        "dashboard_url": run_response.report_url,
                        "status": "running",
                        "created_at": datetime.now().isoformat()
                    }
                    
                    with open("automation_info.json", "w") as f:
                        json.dump(automation_info, f, indent=2)
                    
                    print(f"💾 Automation info saved to: automation_info.json")
                    automated_results = run_response
                    
                except Exception as e:
                    print(f"❌ Error running automated evaluation: {e}")
        
        # Generate manual evaluation form
        manual_file = None
        if manual_items:
            manual_file = self.generate_manual_evaluation_form(manual_items)
        
        # Final summary
        print(f"\n📋 Customized Evaluation Summary:")
        print(f"  🤖 Automated Questions: {len(automated_items)}")
        if automated_results:
            print(f"     Status: Running")
            print(f"     Dashboard: {automated_results.report_url}")
            print(f"     Coverage: Simple conversations, intent recognition, reasoning tasks, multi-task tests")
        
        print(f"  👤 Manual Questions: {len(manual_items)}")
        if manual_file:
            print(f"     Form: {manual_file}")
            print(f"     Coverage: Complex data calculation, memory tests, file search")
        
        print(f"\n🎯 Next Steps:")
        print(f"  1. ⏳ Wait for automated evaluation to complete (check dashboard)")
        print(f"  2. 📝 Complete manual evaluation form:")
        print(f"     - Question 9: Verify humidity calculation against your data")
        print(f"     - Questions 17-18: Evaluate memory/context handling")
        print(f"     - Questions 19-20: Check file search accuracy against your IoT files")
        print(f"  3. 📊 Combine automated + manual results for comprehensive assessment")
        
        print(f"\n💡 Manual Evaluation Tips:")
        print(f"  • Don't penalize reasoning models for showing work - it's transparency!")
        print(f"  • Complex tasks should favor reasoning models (per OpenAI guidance)")
        print(f"  • File search requires checking against your actual data files")
        print(f"  • Focus on task completion and model-appropriate strengths")
        
        return {
            'automated_results': automated_results,
            'manual_file': manual_file,
            'automated_questions': [item['question_id'] for item in automated_items],
            'manual_questions': [item['question_id'] for item in manual_items]
        }

def main():
    """Main function"""
    
    try:
        evaluator = CustomizedHybridEvaluator()
        
        # Use your specific expert file
        expert_file = "expert_evaluation_form_20250805_140600.json"
        if not os.path.exists(expert_file):
            print(f"❌ Expert file not found: {expert_file}")
            return False
        
        results = evaluator.run_customized_evaluation(expert_file)
        
        print(f"\n🎉 Customized hybrid evaluation setup complete!")
        print(f"✨ Perfect balance:")
        print(f"  • 75% automated (15/20 questions) - efficient and consistent")
        print(f"  • 25% manual (5/20 questions) - accuracy where it matters")
        print(f"  • Fair evaluation principles applied throughout")
        print(f"  • Respect for different model design philosophies")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)