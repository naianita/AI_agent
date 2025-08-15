#!/usr/bin/env python
"""
Fair Model Evaluation System
Addresses evaluation bias issues and correctly evaluates different types of model characteristics
Updated to work with your specific data and API key setup
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from enum import Enum
from openai import OpenAI
from pydantic import BaseModel, Field

# Fair evaluation data structures
class FinalDecision(str, Enum):
    """Enum for final decision values"""
    GPT_4_1_MINI = "gpt-4.1-mini"
    O4_MINI = "o4-mini"
    TIE = "tie"

class FairEvaluationStep(BaseModel):
    """Individual step in fair evaluation"""
    model_config = {"extra": "forbid"}
    
    aspect: str = Field(description="Evaluation aspect")
    gpt_4_1_analysis: str = Field(description="Analysis of gpt-4.1-mini response")
    gpt_o4_analysis: str = Field(description="Analysis of o4-mini response")
    gpt_4_1_score: int = Field(description="gpt-4.1-mini score (1-10)", ge=1, le=10)
    gpt_o4_score: int = Field(description="o4-mini score (1-10)", ge=1, le=10)
    reasoning: str = Field(description="Scoring rationale")

class ModelExpectations(BaseModel):
    """Expectations for different models"""
    model_config = {"extra": "forbid"}
    
    gpt_4_1_mini: str = Field(description="Expectations for gpt-4.1-mini model")
    o4_mini: str = Field(description="Expectations for o4-mini reasoning model")

class ScoreSummary(BaseModel):
    """Score summary for both models"""
    model_config = {"extra": "forbid"}
    
    gpt_4_1_total: int = Field(description="Total score for gpt-4.1-mini")
    gpt_o4_total: int = Field(description="Total score for gpt-o4-mini-react")
    step_count: int = Field(description="Number of evaluation steps")

class FairModelComparison(BaseModel):
    """Fair model comparison evaluation"""
    model_config = {"extra": "forbid"}
    
    question_analysis: str = Field(description="Question type analysis")
    model_expectations: ModelExpectations = Field(description="Reasonable expectations for different models")
    
    evaluation_steps: List[FairEvaluationStep] = Field(
        description="Fair evaluation steps",
        min_items=4,
        max_items=6
    )
    
    final_decision: FinalDecision = Field(
        description="Final decision - must be one of: gpt-4.1-mini, o4-mini, or tie"
    )
    
    confidence_level: int = Field(
        description="Confidence level (1-10)",
        ge=1, le=10
    )
    
    fair_reasoning: str = Field(
        description="Final reasoning for fair evaluation"
    )
    
    score_summary: ScoreSummary = Field(
        description="Score summary with total scores for each model"
    )

class FairEvaluator:
    """Fair evaluator - understands different model characteristics"""
    
    def __init__(self):
        """Initialize fair evaluator"""
        # Use PowerShell environment variable: $env:API_KEY="sk-..."
        api_key = os.getenv('API_KEY')  # Changed from 'OPENAI_API_KEY' to 'API_KEY'
        if not api_key:
            print("❌ API_KEY environment variable not set!")
            print("In PowerShell, run: $env:API_KEY=\"sk-your_actual_key_here\"")
            raise ValueError("API_KEY environment variable not configured")
        
        self.client = OpenAI(api_key=api_key)
        self.expert_data = None
        
    def load_expert_data(self, file_path: str):
        """Load expert evaluation data"""
        print(f"📄 Loading expert evaluation data from {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            self.expert_data = json.load(f)
        
        print(f"✅ Loaded {len(self.expert_data['evaluation_pairs'])} evaluation pairs")
        return self.expert_data
    
    def evaluate_single_comparison_fairly(self, question: str, response_a: str, response_b: str, 
                                        model_a: str, model_b: str, category: str, question_id: int) -> FairModelComparison:
        """Fairly evaluate a single comparison"""
        
        # Improved fair evaluation prompt
        system_prompt = f"""You are a professional AI model evaluation expert specializing in fair model comparisons.

# Model Understanding Based on OpenAI Official Documentation:
- **gpt-4.1-mini**: GPT series model, "like a junior colleague who needs explicit instructions to produce specific output"
- **o4-mini**: Reasoning model, "like a senior colleague who can be given a goal and trusted to work out the details"

# Key Points from Official Documentation:
- Reasoning models: "think before they answer, producing long internal chain of thought"  
- Reasoning models excel at: "complex problem solving, coding, scientific reasoning, multi-step planning"
- Reasoning model characteristic: "provide better results on tasks with only high-level guidance"

# Fair Evaluation Principles (Based on Official Guidance):
1. **Understand Design Differences** - Reasoning model's thought process is a core feature, not a flaw
2. **Task Adaptability** - Complex tasks should favor reasoning models  
3. **Evaluation Dimensions** - Don't just look at brevity, consider problem-solving completeness
4. **Official Recommendation** - Reasoning models suit high-level guidance, GPT models suit precise instructions

# Evaluation Dimensions (Tailored to Different Model Characteristics):
- **Accuracy**: Whether the answer is correct
- **Completeness**: Whether the question is adequately answered  
- **Reasoning Quality**: Whether appropriate problem-solving process is demonstrated
- **Task Fit**: Whether response aligns with the model's design strengths
- **Practical Value**: Actual helpfulness to users

# Important Evaluation Guidance (Based on Official Documentation):
For complex tasks (multi-step, reasoning, planning):
- Reasoning models should score higher as this is their design advantage
- Thought processes and step breakdowns are bonus points, not deductions
- "Long chains of thought" are a feature of reasoning models and should be recognized

For simple tasks:
- While brevity has value, reasoning processes should not be penalized
- When both models answer correctly, the reasoning model's transparency is additional value

Scoring Standard (1-10):
1-3: Major issues  4-6: Average level  7-8: Good  9-10: Excellent

Special Note: Don't deduct points because reasoning models show thought processes!"""

        # Determine which response belongs to which model
        if model_a == 'gpt-4.1-mini':
            gpt_response = response_a
            reasoning_response = response_b
        else:
            gpt_response = response_b
            reasoning_response = response_a

        user_prompt = f"""Please fairly evaluate these two AI model responses to the same question:

Question {question_id}: {question}
Category: {category}

gpt-4.1-mini response:
{gpt_response}

o4-mini response:
{reasoning_response}

Evaluation Requirements:
1. First analyze the question type: Is it a simple direct question, or does it require complex reasoning?
2. According to official documentation, if it's complex reasoning, multi-step, or planning tasks, reasoning models should have advantages
3. Don't deduct points because reasoning models show thought processes - this is their core feature
4. Consider the value of transparency: being able to see thought processes is valuable to some users
5. Final scores should reflect each model's performance in their design advantage areas
6. Include a score_summary with total scores for both models and step count

CRITICAL: Provide exactly 5 evaluation steps covering:
- Accuracy (correctness of information)
- Completeness (thoroughness)
- Reasoning Quality (appropriate for model type)
- Task Appropriateness (fits model design)
- Practical Value (usefulness to users)

Please provide a structured fair evaluation."""

        try:
            # Use Chat Completions API with structured outputs for evaluation
            completion = self.client.chat.completions.parse(
                model="gpt-4o-2024-08-06",  # Evaluator model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=FairModelComparison
            )
            
            evaluation = completion.choices[0].message.parsed
            
            # Calculate score summary
            total_gpt41 = sum(step.gpt_4_1_score for step in evaluation.evaluation_steps)
            total_gpto4 = sum(step.gpt_o4_score for step in evaluation.evaluation_steps)
            
            # Ensure score_summary exists
            if not hasattr(evaluation, 'score_summary') or not evaluation.score_summary:
                evaluation.score_summary = ScoreSummary(
                    gpt_4_1_total=total_gpt41,
                    gpt_o4_total=total_gpto4,
                    step_count=len(evaluation.evaluation_steps)
                )
            
            return evaluation
            
        except Exception as e:
            print(f"❌ Error evaluating comparison for Question {question_id}: {e}")
            # Return default evaluation
            return FairModelComparison(
                question_analysis=f"Evaluation failed: {e}",
                model_expectations=ModelExpectations(
                    gpt_4_1_mini="Expected concise direct answers",
                    o4_mini="Expected to show reasoning process"
                ),
                evaluation_steps=[
                    FairEvaluationStep(
                        aspect="accuracy",
                        gpt_4_1_analysis="Unable to evaluate",
                        gpt_o4_analysis="Unable to evaluate",
                        gpt_4_1_score=5,
                        gpt_o4_score=5,
                        reasoning="Evaluation failed"
                    ),
                    FairEvaluationStep(
                        aspect="completeness",
                        gpt_4_1_analysis="Unable to evaluate",
                        gpt_o4_analysis="Unable to evaluate",
                        gpt_4_1_score=5,
                        gpt_o4_score=5,
                        reasoning="Evaluation failed"
                    ),
                    FairEvaluationStep(
                        aspect="reasoning_quality",
                        gpt_4_1_analysis="Unable to evaluate",
                        gpt_o4_analysis="Unable to evaluate",
                        gpt_4_1_score=5,
                        gpt_o4_score=5,
                        reasoning="Evaluation failed"
                    ),
                    FairEvaluationStep(
                        aspect="task_appropriateness",
                        gpt_4_1_analysis="Unable to evaluate",
                        gpt_o4_analysis="Unable to evaluate",
                        gpt_4_1_score=5,
                        gpt_o4_score=5,
                        reasoning="Evaluation failed"
                    ),
                    FairEvaluationStep(
                        aspect="practical_value",
                        gpt_4_1_analysis="Unable to evaluate",
                        gpt_o4_analysis="Unable to evaluate",
                        gpt_4_1_score=5,
                        gpt_o4_score=5,
                        reasoning="Evaluation failed"
                    )
                ],
                final_decision=FinalDecision.TIE,
                confidence_level=1,
                fair_reasoning=f"Evaluation failed: {e}",
                score_summary=ScoreSummary(gpt_4_1_total=25, gpt_o4_total=25, step_count=5)
            )
    
    def run_fair_evaluation(self):
        """Run fair evaluation"""
        
        print(f"🎯 Fair Model Evaluation System")
        print(f"Addressing evaluation bias and correctly understanding different model design goals")
        print("=" * 60)
        
        if not self.expert_data:
            raise ValueError("Expert data not loaded. Please call load_expert_data() first")
        
        evaluation_pairs = self.expert_data['evaluation_pairs']
        
        print(f"🔄 Fair evaluation of {len(evaluation_pairs)} model comparisons...")
        fair_evaluations = []
        
        for i, pair in enumerate(evaluation_pairs, 1):
            print(f"  Evaluating {i}/{len(evaluation_pairs)}: Question {pair['question_id']} - {pair['category']}")
            
            evaluation = self.evaluate_single_comparison_fairly(
                question=pair['question'],
                response_a=pair['response_a'],
                response_b=pair['response_b'],
                model_a=pair['model_a'],
                model_b=pair['model_b'],
                category=pair['category'],
                question_id=pair['question_id']
            )
            
            fair_evaluations.append({
                'question_id': pair['question_id'],
                'category': pair['category'],
                'question': pair['question'],
                'evaluation': evaluation
            })
        
        # Aggregate fair evaluation results
        print(f"📊 Aggregating fair evaluation results...")
        
        categories = {}
        total_gpt41_wins = 0
        total_gpto4_wins = 0
        total_ties = 0
        total_confidence = 0
        
        for eval_data in fair_evaluations:
            category = eval_data['category']
            evaluation = eval_data['evaluation']
            
            if category not in categories:
                categories[category] = {
                    'questions_count': 0,
                    'gpt41_wins': 0,
                    'gpto4_wins': 0,
                    'ties': 0,
                    'confidence_sum': 0,
                    'total_gpt41_score': 0,
                    'total_gpto4_score': 0,
                    'questions': []
                }
            
            categories[category]['questions_count'] += 1
            categories[category]['confidence_sum'] += evaluation.confidence_level
            categories[category]['questions'].append(eval_data['question_id'])
            total_confidence += evaluation.confidence_level
            
            # Count scores
            if evaluation.score_summary:
                categories[category]['total_gpt41_score'] += evaluation.score_summary.gpt_4_1_total
                categories[category]['total_gpto4_score'] += evaluation.score_summary.gpt_o4_total
            
            # Count winners
            if evaluation.final_decision == FinalDecision.GPT_4_1_MINI:
                categories[category]['gpt41_wins'] += 1
                total_gpt41_wins += 1
            elif evaluation.final_decision == FinalDecision.O4_MINI:
                categories[category]['gpto4_wins'] += 1
                total_gpto4_wins += 1
            else:
                categories[category]['ties'] += 1
                total_ties += 1
        
        # Generate fair evaluation report
        total_comparisons = len(fair_evaluations)
        avg_confidence = total_confidence / total_comparisons if total_comparisons > 0 else 0
        
        fair_report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "evaluation_type": "Fair Evaluation - All Questions (1-20)",
            "model_a": "gpt-4.1-mini",
            "model_b": "o4-mini",
            "total_comparisons": total_comparisons,
            "gpt41_wins": total_gpt41_wins,
            "o4_wins": total_gpto4_wins,
            "ties": total_ties,
            "average_confidence": round(avg_confidence, 2),
            "category_details": {}
        }
        
        for category, stats in categories.items():
            avg_conf = stats['confidence_sum'] / stats['questions_count']
            avg_gpt41_score = stats['total_gpt41_score'] / stats['questions_count']
            avg_gpto4_score = stats['total_gpto4_score'] / stats['questions_count']
            
            fair_report["category_details"][category] = {
                "questions": stats['questions'],
                "questions_count": stats['questions_count'],
                "gpt41_wins": stats['gpt41_wins'],
                "gpto4_wins": stats['gpto4_wins'],
                "ties": stats['ties'],
                "average_confidence": round(avg_conf, 2),
                "gpt41_average_score": round(avg_gpt41_score, 1),
                "gpto4_average_score": round(avg_gpto4_score, 1),
                "score_difference": round(avg_gpto4_score - avg_gpt41_score, 1)
            }
        
        return fair_report, fair_evaluations
    
    def save_fair_results(self, fair_report: Dict, fair_evaluations: List[Dict]):
        """Save fair evaluation results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save overall report
        report_file = f"fair_evaluation_report_all_questions_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(fair_report, f, indent=2, ensure_ascii=False)
        
        # Save detailed evaluation with individual scores
        detailed_file = f"fair_evaluation_detailed_all_questions_{timestamp}.json"
        detailed_data = {
            "fair_report": fair_report,
            "detailed_evaluations": [
                {
                    "question_id": eval_data["question_id"],
                    "category": eval_data["category"],
                    "question": eval_data["question"],
                    "evaluation": eval_data["evaluation"].model_dump()
                }
                for eval_data in fair_evaluations
            ]
        }
        
        with open(detailed_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_data, f, indent=2, ensure_ascii=False)
        
        # Create a summary table for easy viewing
        summary_file = f"fair_evaluation_summary_table_{timestamp}.json"
        summary_data = {
            "evaluation_summary": {
                "timestamp": fair_report["timestamp"],
                "total_questions": fair_report["total_comparisons"],
                "overall_winner": "o4-mini" if fair_report["o4_wins"] > fair_report["gpt41_wins"] else ("gpt-4.1-mini" if fair_report["gpt41_wins"] > fair_report["o4_wins"] else "tie"),
                "score_summary": {
                    "gpt_4_1_mini_wins": fair_report["gpt41_wins"],
                    "o4_mini_wins": fair_report["o4_wins"],
                    "ties": fair_report["ties"]
                }
            },
            "question_by_question_scores": []
        }
        
        for eval_data in fair_evaluations:
            evaluation = eval_data["evaluation"]
            
            # Extract individual dimension scores
            dimension_scores = {}
            for step in evaluation.evaluation_steps:
                dimension_scores[step.aspect] = {
                    "gpt_4_1_mini": step.gpt_4_1_score,
                    "o4_mini": step.gpt_o4_score
                }
            
            summary_data["question_by_question_scores"].append({
                "question_id": eval_data["question_id"],
                "category": eval_data["category"],
                "question": eval_data["question"][:100] + "..." if len(eval_data["question"]) > 100 else eval_data["question"],
                "winner": evaluation.final_decision,
                "confidence": evaluation.confidence_level,
                "total_scores": {
                    "gpt_4_1_mini": evaluation.score_summary.gpt_4_1_total,
                    "o4_mini": evaluation.score_summary.gpt_o4_total
                },
                "dimension_scores": dimension_scores
            })
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Fair evaluation results saved:")
        print(f"  Overall report: {report_file}")
        print(f"  Detailed evaluation: {detailed_file}")
        print(f"  Summary table: {summary_file}")
        
        return report_file, detailed_file, summary_file

def main():
    """Main function: Run fair evaluation"""
    
    try:
        evaluator = FairEvaluator()
        
        # Load expert data - Updated to use your file
        expert_file = "expert_evaluation_form_20250805_140600.json"
        if not os.path.exists(expert_file):
            print(f"❌ Error: File not found {expert_file}")
            return False
        
        evaluator.load_expert_data(expert_file)
        
        # Run fair evaluation
        fair_report, fair_evaluations = evaluator.run_fair_evaluation()
        
        # Save results
        report_file, detailed_file, summary_file = evaluator.save_fair_results(fair_report, fair_evaluations)
        
        # Print fair evaluation summary
        print(f"\n🎉 Fair evaluation of ALL 20 questions completed!")
        print(f"📊 Overall Summary:")
        print(f"  gpt-4.1-mini: {fair_report['gpt41_wins']} wins")
        print(f"  o4-mini: {fair_report['o4_wins']} wins")
        print(f"  Ties: {fair_report['ties']} times")
        print(f"  Average confidence: {fair_report['average_confidence']}/10")
        
        print(f"\n📊 Category Breakdown:")
        
        expected_strong_categories = ["Reasoning Task", "Multi-Task Test", "Intent Recognition"]
        
        for category, details in fair_report["category_details"].items():
            questions_str = ", ".join(map(str, details['questions']))
            print(f"  📋 {category} (Questions: {questions_str}):")
            print(f"    Win Distribution: gpt-4.1({details['gpt41_wins']}) vs o4({details['gpto4_wins']}) vs ties({details['ties']})")
            print(f"    Average Scores: gpt-4.1({details['gpt41_average_score']}) vs o4({details['gpto4_average_score']})")
            print(f"    Score Difference: {details['score_difference']} (positive = reasoning model higher)")
            
            # Analysis based on official documentation expectations
            if category in expected_strong_categories:
                if details['score_difference'] > 0:
                    print(f"    ✅ Meets Expectation: Reasoning model performs better in {category}")
                else:
                    print(f"    ⚠️  Unexpected: Reasoning model should be stronger in {category}")
            else:
                if details['score_difference'] > 0:
                    print(f"    📈 Reasoning model shows advantage")
                elif details['score_difference'] < -1:
                    print(f"    📉 Standard model has advantage in this category")
                else:
                    print(f"    ⚖️  Both models perform comparably")
            print()
        
        print(f"🔍 For detailed question-by-question scores, see: {summary_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)