#!/usr/bin/env python
"""
Bias-Controlled Model Evaluation
Uses multiple choice format with shuffling to eliminate position bias
"""

import json
import os
import random
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
from openai import OpenAI
from pathlib import Path

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path(".env")
    if env_file.exists():
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.replace('\x00', '').strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip().replace('\x00', '')
                        value = value.strip().replace('\x00', '')
                        if key and value:
                            os.environ[key] = value
        except Exception as e:
            print(f"Warning: Could not load .env file: {e}")

# Load .env file at startup
load_env_file()

def make_abc(answers: List[str], *, correct_idx: int = 0, shuffle: bool = True, rng: Optional[random.Random] = None) -> Tuple[str, str]:
    """
    Create multiple choice options with bias control
    
    ARGS:
    - answers: List of answer choices (model responses)
    - correct_idx: Index of the "correct" answer (for tracking)
    - shuffle: If True, randomize order to prevent position bias
    - rng: Random number generator for consistent shuffling
    
    RETURNS:
    - (options_string, correct_letter): Formatted options and correct answer letter
    """
    p = list(range(len(answers)))
    if shuffle:
        if rng is None:
            raise ValueError("shuffle=True requires rng")
        rng.shuffle(p)
    
    options = ""
    for i, j in enumerate(p):
        if i > 0:
            options += "\n"
        options += chr(ord("A") + i) + ") " + answers[j]
    
    return options, chr(ord("A") + p.index(correct_idx))

class BiasControlledEvaluator:
    def __init__(self):
        """Initialize bias-controlled evaluator"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=api_key)
        self.expert_data = None
        
    def load_expert_data(self, file_path: str):
        """Load expert evaluation data"""
        print(f"📄 Loading expert evaluation data from {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            self.expert_data = json.load(f)
        
        print(f"✅ Loaded {len(self.expert_data['evaluation_pairs'])} evaluation pairs")
        return self.expert_data
    
    def create_bias_controlled_samples(self, criteria_name: str) -> List[Dict[str, Any]]:
        """Create evaluation samples with bias control using make_abc"""
        
        if not self.expert_data:
            raise ValueError("Expert data not loaded. Call load_expert_data() first.")
        
        evaluation_pairs = self.expert_data['evaluation_pairs']
        criteria_description = self.expert_data['evaluation_criteria'][criteria_name]
        
        samples = []
        
        for i, pair in enumerate(evaluation_pairs):
            # Create RNG with consistent seed for this question
            rng = random.Random(f"question_{i}_{criteria_name}")
            
            # Prepare answers (model responses)
            answers = [
                f"Response from {pair['model_a']}:\n{pair['response_a']}",
                f"Response from {pair['model_b']}:\n{pair['response_b']}"
            ]
            
            # Create multiple choice with randomization
            options, correct_letter = make_abc(
                answers=answers,
                correct_idx=0,  # We'll track which is which separately
                shuffle=True,
                rng=rng
            )
            
            # Track original mapping for analysis
            shuffled_order = list(range(len(answers)))
            rng_copy = random.Random(f"question_{i}_{criteria_name}")
            rng_copy.shuffle(shuffled_order)
            
            sample = {
                "question_id": pair['question_id'],
                "category": pair['category'],
                "question": pair['question'],
                "criteria": criteria_description,
                "options": options,
                "original_model_a": pair['model_a'],
                "original_model_b": pair['model_b'],
                "original_response_a": pair['response_a'],
                "original_response_b": pair['response_b'],
                "shuffled_order": shuffled_order,  # [0,1] or [1,0] depending on shuffle
                "memory_context": pair.get('memory_context'),
                "randomization_seed": f"question_{i}_{criteria_name}"
            }
            
            samples.append(sample)
        
        return samples
    
    def create_advanced_eval_with_bias_control(self, criteria_name: str):
        """Create evaluation using bias-controlled multiple choice format"""
        
        criteria_description = self.expert_data['evaluation_criteria'][criteria_name]
        
        eval_config = {
            "name": f"Bias-Controlled Model Comparison - {criteria_name.replace('_', ' ').title()}",
            "data_source_config": {
                "type": "custom",
                "item_schema": {
                    "type": "object",
                    "properties": {
                        "question_id": {"type": "integer"},
                        "category": {"type": "string"},
                        "question": {"type": "string"},
                        "criteria": {"type": "string"},
                        "options": {"type": "string"},
                        "original_model_a": {"type": "string"},
                        "original_model_b": {"type": "string"},
                        "shuffled_order": {"type": "array"},
                        "randomization_seed": {"type": "string"}
                    },
                    "required": ["question", "options", "criteria"]
                },
                "include_sample_schema": True
            },
            "testing_criteria": [
                {
                    "type": "score_model",
                    "name": f"{criteria_name}_bias_controlled_grader",
                    "model": "gpt-4.1",
                    "input": [
                        {
                            "role": "system",
                            "content": f"""You are an expert evaluator comparing AI model responses with bias control.

EVALUATION CRITERIA: {criteria_description}

INSTRUCTIONS:
- You will see a question and multiple response options (A, B, etc.)
- Evaluate which response better meets the criteria
- The options are randomly ordered to prevent position bias
- Choose the letter of the best response
- If responses are truly equivalent, choose the first one (A)

FORMAT: Respond with exactly one letter (A, B, C, etc.)"""
                        },
                        {
                            "role": "user",
                            "content": """Question: {{{{ sample.question }}}}
Category: {{{{ sample.category }}}}

Evaluation Criteria: {{{{ sample.criteria }}}}

Response Options:
{{{{ sample.options }}}}

Which response better meets the evaluation criteria? Respond with the letter only (A, B, etc.)."""
                        }
                    ],
                    "range": [1, 5],
                    "pass_threshold": 3.0
                }
            ]
        }
        
        return eval_config
    
    def run_bias_controlled_evaluation(self, criteria_name: str = "overall_preference"):
        """Run bias-controlled evaluation with multiple choice format"""
        
        print(f"🎯 BIAS-CONTROLLED MODEL EVALUATION")
        print(f"Using multiple choice format with randomization")
        print(f"Criteria: {criteria_name}")
        print("=" * 60)
        
        if not self.expert_data:
            raise ValueError("Expert data not loaded. Call load_expert_data() first.")
        
        # Create bias-controlled samples
        print("🔄 Creating bias-controlled evaluation samples...")
        samples = self.create_bias_controlled_samples(criteria_name)
        print(f"✅ Created {len(samples)} bias-controlled samples")
        
        # Show example of bias control
        example = samples[0]
        print(f"\n📋 BIAS CONTROL EXAMPLE:")
        print(f"Question: {example['question'][:50]}...")
        print(f"Original Order: {example['original_model_a']} vs {example['original_model_b']}")
        print(f"Shuffled Order: {example['shuffled_order']}")
        print(f"Options Preview:")
        print(example['options'][:200] + "...")
        
        # Prepare data for upload
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        items = [{"sample": sample} for sample in samples]
        
        # Save test data
        test_file_path = f"bias_controlled_test_data_{criteria_name}_{timestamp}.jsonl"
        with open(test_file_path, 'w', encoding='utf-8') as f:
            for item in items:
                f.write(json.dumps(item) + '\n')
        
        print(f"💾 Saved test data: {test_file_path}")
        
        # Upload to OpenAI
        print("📤 Uploading to OpenAI...")
        with open(test_file_path, 'rb') as f:
            uploaded_file = self.client.files.create(
                file=f,
                purpose="evals"
            )
        print(f"✅ File uploaded: {uploaded_file.id}")
        
        # Create evaluation
        print("🛠️ Creating bias-controlled evaluation...")
        eval_config = self.create_advanced_eval_with_bias_control(criteria_name)
        
        try:
            eval_obj = self.client.evals.create(**eval_config)
            print(f"✅ Eval created: {eval_obj.id}")
        except Exception as e:
            print(f"❌ Eval creation failed: {e}")
            return None
        
        # Run evaluation
        print("🏃 Starting bias-controlled evaluation...")
        try:
            eval_run = self.client.evals.runs.create(
                eval_obj.id,
                name=f"Bias-Controlled {criteria_name} Analysis",
                data_source={
                    "type": "jsonl",
                    "source": {
                        "type": "file_id",
                        "id": uploaded_file.id
                    }
                }
            )
            
            print(f"✅ Evaluation started successfully!")
            print(f"🆔 Eval ID: {eval_obj.id}")
            print(f"🆔 Run ID: {eval_run.id}")
            print(f"📊 Status: {eval_run.status}")
            print(f"🔗 Dashboard: {eval_run.report_url}")
            
            # Save analysis metadata
            metadata = {
                "timestamp": timestamp,
                "criteria": criteria_name,
                "eval_id": eval_obj.id,
                "run_id": eval_run.id,
                "report_url": eval_run.report_url,
                "test_file": test_file_path,
                "bias_control": {
                    "method": "multiple_choice_shuffling",
                    "randomization": "per_question_seed",
                    "shuffle_function": "make_abc"
                },
                "sample_count": len(samples)
            }
            
            metadata_file = f"bias_controlled_metadata_{criteria_name}_{timestamp}.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"💾 Analysis metadata saved: {metadata_file}")
            
            return metadata
            
        except Exception as e:
            print(f"❌ Eval run failed: {e}")
            return None

def main():
    """Main function for bias-controlled evaluation"""
    
    try:
        evaluator = BiasControlledEvaluator()
        
        # Load expert data
        expert_file = "expert_evaluation_form_20250805_003609.json"
        if not os.path.exists(expert_file):
            print(f"❌ Error: {expert_file} not found")
            return False
        
        evaluator.load_expert_data(expert_file)
        
        # Run bias-controlled analysis
        criteria = "overall_preference"  # Can be changed
        result = evaluator.run_bias_controlled_evaluation(criteria)
        
        if result:
            print(f"\n🎉 BIAS-CONTROLLED EVALUATION SUCCESS!")
            print(f"📊 Key Features:")
            print(f"  ✅ Position bias eliminated via shuffling")
            print(f"  ✅ Consistent randomization per question")
            print(f"  ✅ Multiple choice format")
            print(f"  ✅ Detailed tracking for analysis")
            print(f"\n🔗 Monitor results: {result['report_url']}")
            
            return True
        else:
            print(f"\n❌ Evaluation failed to start")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)