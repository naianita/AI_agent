#!/usr/bin/env python
"""
Robust JSON Fixer
Fixes JSON syntax errors caused by unescaped content in text fields
"""

import json
import re
import os
def create_fixed_manual_evaluation():
    """Create a properly formatted manual evaluation file"""
    
    print("🔧 Creating properly formatted manual evaluation file...")
    
    # Your manual evaluation data in proper Python format
    manual_data = {
        "evaluation_info": {
            "type": "Manual Evaluation - Questions 9, 17-20",
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
        "evaluation_items": [
            {
                "question_id": 9,
                "category": "Reasoning Task",
                "question": "Using your humidity historical data, calculate the average from any 7-day period and compare to optimal ranges (30-50%).",
                "context": "Data calculation task - requires verifying actual humidity data and mathematical accuracy",
                "responses": {
                    "gpt_4_1_mini": {
                        "text": "GPT provided sample humidity data and calculated 42.21% average (may not be from actual data)",
                        "expected_characteristics": "Direct, concise answer with environmental expertise"
                    },
                    "o4_mini_reasoning": {
                        "text": "Reasoning model searched actual data, found only single day available, refused to fabricate 7-day calculation",
                        "expected_characteristics": "Step-by-step reasoning process showing explicit thinking"
                    }
                },
                "evaluation_dimensions": {
                    "accuracy": {
                        "description": "Correctness of information and calculations",
                        "gpt_score": 1,
                        "reasoning_score": 10,
                        "notes": ""
                    },
                    "completeness": {
                        "description": "How thoroughly the question is addressed",
                        "gpt_score": 1,
                        "reasoning_score": 10,
                        "notes": ""
                    },
                    "task_appropriateness": {
                        "description": "How well response matches model's design strengths",
                        "gpt_score": 3,
                        "reasoning_score": 10,
                        "notes": "Consider: complex tasks should favor reasoning models"
                    },
                    "transparency": {
                        "description": "Clarity of reasoning and process visibility",
                        "gpt_score": 1,
                        "reasoning_score": 10,
                        "notes": "Reasoning model's visible process is a feature, not verbosity"
                    },
                    "practical_value": {
                        "description": "Real-world usefulness to users",
                        "gpt_score": 1,
                        "reasoning_score": 10,
                        "notes": ""
                    }
                },
                "overall_assessment": {
                    "preferred_model": "o4-mini",
                    "confidence": 10,
                    "reasoning": "Reasoning model correctly identified data limitations and refused to fabricate information",
                    "bias_check": ""
                }
            },
            {
                "question_id": 17,
                "category": "Memory Test",
                "question": "From your historical CO2 data, if levels were 720 ppm on a Wednesday, what does that indicate?",
                "context": "Memory test baseline - establishes context for question 18",
                "responses": {
                    "gpt_4_1_mini": {
                        "text": "GPT provided general CO2 assessment and recommendations",
                        "expected_characteristics": "Direct, concise answer with environmental expertise"
                    },
                    "o4_mini_reasoning": {
                        "text": "Reasoning model searched data, found specific Wednesday entry, provided detailed analysis and recommendations",
                        "expected_characteristics": "Step-by-step reasoning process showing explicit thinking"
                    }
                },
                "evaluation_dimensions": {
                    "accuracy": {
                        "description": "Correctness of information and calculations",
                        "gpt_score": 8,
                        "reasoning_score": 10,
                        "notes": ""
                    },
                    "completeness": {
                        "description": "How thoroughly the question is addressed",
                        "gpt_score": 10,
                        "reasoning_score": 10,
                        "notes": ""
                    },
                    "task_appropriateness": {
                        "description": "How well response matches model's design strengths",
                        "gpt_score": 9,
                        "reasoning_score": 10,
                        "notes": "Consider: complex tasks should favor reasoning models"
                    },
                    "transparency": {
                        "description": "Clarity of reasoning and process visibility",
                        "gpt_score": 8,
                        "reasoning_score": 10,
                        "notes": "Reasoning model's visible process is a feature, not verbosity"
                    },
                    "practical_value": {
                        "description": "Real-world usefulness to users",
                        "gpt_score": 8,
                        "reasoning_score": 10,
                        "notes": ""
                    }
                },
                "overall_assessment": {
                    "preferred_model": "o4-mini",
                    "confidence": 10,
                    "reasoning": "remember previous conversation and give suggestion",
                    "bias_check": ""
                }
            },
            {
                "question_id": 18,
                "category": "Memory Test",
                "question": "Based on that CO2 level you just analyzed, are those conditions safe for children?",
                "context": "Memory test follow-up - requires understanding context from question 17",
                "responses": {
                    "gpt_4_1_mini": {
                        "text": "GPT provided safety assessment for children at 720 ppm CO2",
                        "expected_characteristics": "Direct, concise answer with environmental expertise"
                    },
                    "o4_mini_reasoning": {
                        "text": "Reasoning model referenced previous analysis, provided detailed children-specific safety assessment with recommendations",
                        "expected_characteristics": "Step-by-step reasoning process showing explicit thinking"
                    }
                },
                "evaluation_dimensions": {
                    "accuracy": {
                        "description": "Correctness of information and calculations",
                        "gpt_score": 10,
                        "reasoning_score": 10,
                        "notes": ""
                    },
                    "completeness": {
                        "description": "How thoroughly the question is addressed",
                        "gpt_score": 9,
                        "reasoning_score": 10,
                        "notes": ""
                    },
                    "task_appropriateness": {
                        "description": "How well response matches model's design strengths",
                        "gpt_score": 10,
                        "reasoning_score": 10,
                        "notes": "Consider: complex tasks should favor reasoning models"
                    },
                    "transparency": {
                        "description": "Clarity of reasoning and process visibility",
                        "gpt_score": 10,
                        "reasoning_score": 10,
                        "notes": "Reasoning model's visible process is a feature, not verbosity"
                    },
                    "practical_value": {
                        "description": "Real-world usefulness to users",
                        "gpt_score": 9,
                        "reasoning_score": 10,
                        "notes": ""
                    }
                },
                "overall_assessment": {
                    "preferred_model": "o4-mini",
                    "confidence": 10,
                    "reasoning": "remember previous conversation and give suggestion",
                    "bias_check": ""
                }
            },
            {
                "question_id": 19,
                "category": "File Search Test",
                "question": "Search your IoT sensor files and tell me the exact CO2 reading from sensor ID 14 on December 16, 2024 at 18:40. Include the file name where you found this data.",
                "context": "File search accuracy test - requires verification against actual IoT data files",
                "responses": {
                    "gpt_4_1_mini": {
                        "text": "GPT found CO2 reading 443.0 ppm at 18:40:12 from iot_co2_data.json",
                        "expected_characteristics": "Direct, concise answer with environmental expertise"
                    },
                    "o4_mini_reasoning": {
                        "text": "Reasoning model showed search process, found same result: 443.0 ppm at 18:40:12 from iot_co2_data.json",
                        "expected_characteristics": "Step-by-step reasoning process showing explicit thinking"
                    }
                },
                "evaluation_dimensions": {
                    "accuracy": {
                        "description": "Correctness of information and calculations",
                        "gpt_score": 10,
                        "reasoning_score": 10,
                        "notes": ""
                    },
                    "completeness": {
                        "description": "How thoroughly the question is addressed",
                        "gpt_score": 10,
                        "reasoning_score": 10,
                        "notes": ""
                    },
                    "task_appropriateness": {
                        "description": "How well response matches model's design strengths",
                        "gpt_score": 8,
                        "reasoning_score": 10,
                        "notes": "Consider: complex tasks should favor reasoning models"
                    },
                    "transparency": {
                        "description": "Clarity of reasoning and process visibility",
                        "gpt_score": 9,
                        "reasoning_score": 10,
                        "notes": "Reasoning model's visible process is a feature, not verbosity"
                    },
                    "practical_value": {
                        "description": "Real-world usefulness to users",
                        "gpt_score": 10,
                        "reasoning_score": 10,
                        "notes": ""
                    }
                },
                "overall_assessment": {
                    "preferred_model": "o4-mini",
                    "confidence": 10,
                    "reasoning": "reply the right answer direct and clear",
                    "bias_check": ""
                }
            },
            {
                "question_id": 20,
                "category": "File Search Test",
                "question": "From your historical sensor data files, find the highest TVOC reading recorded and tell me: the exact value, sensor ID, date/time, and which specific file contained this information.",
                "context": "File search comprehensive test - requires finding maximum values in actual data",
                "responses": {
                    "gpt_4_1_mini": {
                        "text": "GPT found highest TVOC: 15.0 ppb, Sensor 14, 2024-12-16 19:58:04",
                        "expected_characteristics": "Direct, concise answer with environmental expertise"
                    },
                    "o4_mini_reasoning": {
                        "text": "Reasoning model found highest TVOC: 915 ppb, sensor tvoc-4, 2025-07-15 13:45:00 (different result)",
                        "expected_characteristics": "Step-by-step reasoning process showing explicit thinking"
                    }
                },
                "evaluation_dimensions": {
                    "accuracy": {
                        "description": "Correctness of information and calculations",
                        "gpt_score": 10,
                        "reasoning_score": 0,
                        "notes": ""
                    },
                    "completeness": {
                        "description": "How thoroughly the question is addressed",
                        "gpt_score": 10,
                        "reasoning_score": 0,
                        "notes": ""
                    },
                    "task_appropriateness": {
                        "description": "How well response matches model's design strengths",
                        "gpt_score": 10,
                        "reasoning_score": 5,
                        "notes": "Consider: complex tasks should favor reasoning models"
                    },
                    "transparency": {
                        "description": "Clarity of reasoning and process visibility",
                        "gpt_score": 10,
                        "reasoning_score": 5,
                        "notes": "Reasoning model's visible process is a feature, not verbosity"
                    },
                    "practical_value": {
                        "description": "Real-world usefulness to users",
                        "gpt_score": 10,
                        "reasoning_score": 0,
                        "notes": ""
                    }
                },
                "overall_assessment": {
                    "preferred_model": "gpt-4.1-mini",
                    "confidence": 10,
                    "reasoning": "reply the right answer",
                    "bias_check": ""
                }
            }
        ]
    }
    
    # Save as properly formatted JSON
    output_file = "manual_evaluation_questions_9_17-20_20250805_160806_FIXED.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(manual_data, f, indent=2, ensure_ascii=False)
    
    # Verify it's valid JSON
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            json.load(f)
        print(f"✅ Created valid JSON file: {output_file}")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Still invalid JSON: {e}")
        return False

def backup_and_replace():
    """Backup original file and replace with fixed version"""
    
    original_file = "manual_evaluation_questions_9_17-20_20250805_160806.json"
    fixed_file = "manual_evaluation_questions_9_17-20_20250805_160806_FIXED.json"
    backup_file = "manual_evaluation_questions_9_17-20_20250805_160806_BACKUP.json"
    
    # Backup original
    if os.path.exists(original_file):
        os.rename(original_file, backup_file)
        print(f"📁 Backed up original as: {backup_file}")
    
    # Replace with fixed version
    if os.path.exists(fixed_file):
        os.rename(fixed_file, original_file)
        print(f"✅ Replaced with fixed version: {original_file}")
        return True
    
    return False

def main():
    """Main function"""
    
    print("🔧 Robust JSON Fixer for Manual Evaluation")
    print("=" * 50)
    
    # Create the fixed file
    if create_fixed_manual_evaluation():
        print("\n🎯 Options:")
        print("1. Keep both files (original + fixed)")
        print("2. Replace original with fixed version")
        
        choice = input("\nChoose option (1 or 2): ").strip()
        
        if choice == "2":
            if backup_and_replace():
                print("\n✅ File replacement complete!")
                print("🚀 Now you can run: python manual_override_combiner.py")
            else:
                print("\n❌ File replacement failed")
        else:
            print("\n📝 Update your combiner to use: manual_evaluation_questions_9_17-20_20250805_160806_FIXED.json")
            print("   Or manually rename the _FIXED file to replace the original")
    
    return True

if __name__ == "__main__":
    main()