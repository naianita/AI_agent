#!/usr/bin/env python
"""
Structured Outputs Model Evaluation
Uses OpenAI's Structured Outputs for reliable, schema-enforced evaluation responses
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from openai import OpenAI
from pydantic import BaseModel, Field

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

# Structured Output Models
class EvaluationStep(BaseModel):
    """Individual step in the evaluation reasoning process"""
    aspect: str = Field(description="What aspect is being evaluated (e.g., accuracy, clarity)")
    analysis: str = Field(description="Detailed analysis of this aspect")
    score_a: int = Field(description="Score for Response A (1-10)", ge=1, le=10)
    score_b: int = Field(description="Score for Response B (1-10)", ge=1, le=10)

class ModelComparison(BaseModel):
    """Structured evaluation comparing two model responses"""
    question_understanding: str = Field(description="Analysis of what the question is asking")
    
    evaluation_steps: List[EvaluationStep] = Field(
        description="Step-by-step evaluation of different aspects",
        min_items=3,
        max_items=7
    )
    
    overall_winner: str = Field(
        description="Which response is better overall",
        pattern="^(Response A|Response B|Equal)$"
    )
    
    confidence_level: int = Field(
        description="Confidence in the decision (1-10)",
        ge=1, le=10
    )
    
    summary_reasoning: str = Field(
        description="Final reasoning summary explaining the decision"
    )
    
    numerical_scores: Optional[Dict[str, int]] = Field(
        description="Final numerical scores",
        default=None
    )

class CategoryAnalysis(BaseModel):
    """Analysis breakdown by question category"""
    category: str = Field(description="Question category (e.g., Mathematical, Health)")
    questions_count: int = Field(description="Number of questions in this category")
    model_a_wins: int = Field(description="Number of wins for Model A")
    model_b_wins: int = Field(description="Number of wins for Model B")
    equal_count: int = Field(description="Number of equal/tie results")
    average_confidence: float = Field(description="Average confidence score")
    key_insights: List[str] = Field(description="Key insights about this category")

class OverallAnalysis(BaseModel):
    """Complete structured analysis of model comparison"""
    timestamp: str = Field(description="Analysis timestamp")
    model_a_name: str = Field(description="Name of Model A")
    model_b_name: str = Field(description="Name of Model B")
    
    total_comparisons: int = Field(description="Total number of comparisons")
    model_a_wins: int = Field(description="Total wins for Model A")
    model_b_wins: int = Field(description="Total wins for Model B")
    equal_results: int = Field(description="Total equal/tie results")
    
    category_breakdown: List[CategoryAnalysis] = Field(description="Analysis by category")
    
    statistical_summary: Optional[Dict[str, float]] = Field(
        description="Statistical measures",
        default=None
    )
    
    key_findings: List[str] = Field(description="Top-level insights and findings")
    recommendations: List[str] = Field(description="Recommendations based on analysis")

class StructuredOutputsEvaluator:
    """Evaluator using OpenAI's Structured Outputs for reliable, schema-enforced results"""
    
    def __init__(self):
        """Initialize the structured outputs evaluator"""
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
    
    def evaluate_single_comparison(self, question: str, response_a: str, response_b: str, 
                                 model_a: str, model_b: str, category: str) -> ModelComparison:
        """Evaluate a single comparison using structured outputs"""
        
        system_prompt = f"""You are an expert AI evaluator specializing in comparing model responses.

Your task is to provide a structured, comprehensive evaluation comparing two AI model responses.

EVALUATION FRAMEWORK:
1. Understand what the question is asking
2. Analyze multiple aspects: accuracy, completeness, clarity, helpfulness, reasoning quality
3. Provide step-by-step scoring (1-10 scale)
4. Make a final decision with confidence level
5. Explain your reasoning clearly

SCORING SCALE:
- 1-3: Poor (major issues, incorrect, unhelpful)  
- 4-6: Average (acceptable but with notable limitations)
- 7-8: Good (high quality, thorough, helpful)
- 9-10: Excellent (exceptional quality, comprehensive, insightful)

Be objective, thorough, and consistent in your evaluation."""

        user_prompt = f"""Compare these two AI model responses:

QUESTION: {question}
CATEGORY: {category}

RESPONSE A ({model_a}):
{response_a}

RESPONSE B ({model_b}):
{response_b}

Provide a comprehensive structured evaluation following the framework."""

        try:
            response = self.client.responses.parse(
                model="gpt-4o-2024-08-06",  # Model that supports Structured Outputs
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                text_format=ModelComparison
            )
            
            evaluation = response.output_parsed
            
            # Calculate numerical scores
            total_a = sum(step.score_a for step in evaluation.evaluation_steps)
            total_b = sum(step.score_b for step in evaluation.evaluation_steps)
            
            evaluation.numerical_scores = {
                "response_a_total": total_a,
                "response_b_total": total_b
            }
            
            return evaluation
            
        except Exception as e:
            print(f"❌ Error evaluating comparison: {e}")
            # Return a default evaluation in case of errors (minimum 3 steps required)
            return ModelComparison(
                question_understanding=f"Error occurred during evaluation: {e}",
                evaluation_steps=[
                    EvaluationStep(
                        aspect="accuracy",
                        analysis="Unable to evaluate due to technical error",
                        score_a=5,
                        score_b=5
                    ),
                    EvaluationStep(
                        aspect="clarity",
                        analysis="Unable to evaluate due to technical error",
                        score_a=5,
                        score_b=5
                    ),
                    EvaluationStep(
                        aspect="helpfulness",
                        analysis="Unable to evaluate due to technical error",
                        score_a=5,
                        score_b=5
                    )
                ],
                overall_winner="Equal",
                confidence_level=1,
                summary_reasoning=f"Evaluation failed: {e}",
                numerical_scores={"response_a_total": 15, "response_b_total": 15}
            )
    
    def run_structured_evaluation(self) -> OverallAnalysis:
        """Run complete structured evaluation using Structured Outputs"""
        
        print(f"🎯 STRUCTURED OUTPUTS MODEL EVALUATION")
        print(f"Using schema-enforced responses for reliable analysis")
        print("=" * 60)
        
        if not self.expert_data:
            raise ValueError("Expert data not loaded. Call load_expert_data() first.")
        
        evaluation_pairs = self.expert_data['evaluation_pairs']
        
        # Run individual comparisons
        print(f"🔄 Evaluating {len(evaluation_pairs)} model comparisons...")
        individual_evaluations = []
        
        for i, pair in enumerate(evaluation_pairs, 1):
            print(f"  Evaluating {i}/{len(evaluation_pairs)}: {pair['category']}")
            
            evaluation = self.evaluate_single_comparison(
                question=pair['question'],
                response_a=pair['response_a'],
                response_b=pair['response_b'],
                model_a=pair['model_a'],
                model_b=pair['model_b'],
                category=pair['category']
            )
            
            individual_evaluations.append({
                'question_id': pair['question_id'],
                'category': pair['category'],
                'evaluation': evaluation
            })
        
        # Aggregate results
        print(f"📊 Aggregating structured results...")
        
        # Count wins by category
        categories = {}
        total_a_wins = 0
        total_b_wins = 0
        total_equal = 0
        total_confidence = 0
        
        for eval_data in individual_evaluations:
            category = eval_data['category']
            evaluation = eval_data['evaluation']
            
            if category not in categories:
                categories[category] = {
                    'questions_count': 0,
                    'model_a_wins': 0,
                    'model_b_wins': 0,
                    'equal_count': 0,
                    'confidence_sum': 0
                }
            
            categories[category]['questions_count'] += 1
            categories[category]['confidence_sum'] += evaluation.confidence_level
            total_confidence += evaluation.confidence_level
            
            if evaluation.overall_winner == "Response A":
                categories[category]['model_a_wins'] += 1
                total_a_wins += 1
            elif evaluation.overall_winner == "Response B":
                categories[category]['model_b_wins'] += 1
                total_b_wins += 1
            else:
                categories[category]['equal_count'] += 1
                total_equal += 1
        
        # Create category analysis
        category_analyses = []
        for category, stats in categories.items():
            avg_confidence = stats['confidence_sum'] / stats['questions_count']
            
            # Generate insights
            insights = []
            if stats['model_a_wins'] > stats['model_b_wins']:
                insights.append(f"Model A performs better in {category} category")
            elif stats['model_b_wins'] > stats['model_a_wins']:
                insights.append(f"Model B performs better in {category} category")
            else:
                insights.append(f"Models perform similarly in {category} category")
            
            insights.append(f"Average confidence: {avg_confidence:.1f}/10")
            
            category_analyses.append(CategoryAnalysis(
                category=category,
                questions_count=stats['questions_count'],
                model_a_wins=stats['model_a_wins'],
                model_b_wins=stats['model_b_wins'],
                equal_count=stats['equal_count'],
                average_confidence=avg_confidence,
                key_insights=insights
            ))
        
        # Generate key findings and recommendations
        total_comparisons = len(individual_evaluations)
        model_a_win_rate = total_a_wins / total_comparisons if total_comparisons > 0 else 0
        avg_confidence = total_confidence / total_comparisons if total_comparisons > 0 else 0
        
        key_findings = [
            f"Model A wins: {total_a_wins}/{total_comparisons} ({model_a_win_rate:.1%})",
            f"Model B wins: {total_b_wins}/{total_comparisons} ({(total_b_wins/total_comparisons):.1%})",
            f"Equal results: {total_equal}/{total_comparisons} ({(total_equal/total_comparisons):.1%})",
            f"Average evaluation confidence: {avg_confidence:.1f}/10"
        ]
        
        recommendations = [
            "Review category-specific performance differences",
            "Analyze low-confidence evaluations for improvement opportunities",
            "Consider model strengths when choosing for specific tasks"
        ]
        
        if model_a_win_rate > 0.6:
            recommendations.append("Model A shows clear advantages across categories")
        elif model_a_win_rate < 0.4:
            recommendations.append("Model B shows clear advantages across categories")
        else:
            recommendations.append("Models perform similarly - consider task-specific factors")
        
        # Create overall analysis
        model_a_name = evaluation_pairs[0]['model_a'] if evaluation_pairs else "Model A"
        model_b_name = evaluation_pairs[0]['model_b'] if evaluation_pairs else "Model B"
        
        overall_analysis = OverallAnalysis(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            model_a_name=model_a_name,
            model_b_name=model_b_name,
            total_comparisons=total_comparisons,
            model_a_wins=total_a_wins,
            model_b_wins=total_b_wins,
            equal_results=total_equal,
            category_breakdown=category_analyses,
            statistical_summary={
                "model_a_win_rate": model_a_win_rate,
                "average_confidence": avg_confidence,
                "decision_certainty": 1.0 - (total_equal / total_comparisons)
            },
            key_findings=key_findings,
            recommendations=recommendations
        )
        
        return overall_analysis, individual_evaluations
    
    def save_results(self, overall_analysis: OverallAnalysis, individual_evaluations: List[Dict]):
        """Save structured results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save overall analysis
        overall_file = f"structured_analysis_overall_{timestamp}.json"
        with open(overall_file, 'w', encoding='utf-8') as f:
            json.dump(overall_analysis.model_dump(), f, indent=2, ensure_ascii=False)
        
        # Save detailed evaluations
        detailed_file = f"structured_analysis_detailed_{timestamp}.json"
        detailed_data = {
            "overall_analysis": overall_analysis.model_dump(),
            "individual_evaluations": [
                {
                    "question_id": eval_data["question_id"],
                    "category": eval_data["category"],
                    "evaluation": eval_data["evaluation"].model_dump()
                }
                for eval_data in individual_evaluations
            ]
        }
        
        with open(detailed_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved:")
        print(f"  Overall analysis: {overall_file}")
        print(f"  Detailed evaluations: {detailed_file}")
        
        return overall_file, detailed_file

def main():
    """Main function for structured outputs evaluation"""
    
    try:
        evaluator = StructuredOutputsEvaluator()
        
        # Load expert data
        expert_file = "expert_evaluation_form_20250805_003609.json"
        if not os.path.exists(expert_file):
            print(f"❌ Error: {expert_file} not found")
            return False
        
        evaluator.load_expert_data(expert_file)
        
        # Run structured evaluation
        overall_analysis, individual_evaluations = evaluator.run_structured_evaluation()
        
        # Save results
        overall_file, detailed_file = evaluator.save_results(overall_analysis, individual_evaluations)
        
        # Print summary
        print(f"\n🎉 STRUCTURED EVALUATION COMPLETE!")
        print(f"📊 SUMMARY:")
        print(f"  {overall_analysis.model_a_name}: {overall_analysis.model_a_wins} wins")
        print(f"  {overall_analysis.model_b_name}: {overall_analysis.model_b_wins} wins")
        print(f"  Equal: {overall_analysis.equal_results} results")
        print(f"  Average confidence: {overall_analysis.statistical_summary['average_confidence']:.1f}/10")
        
        print(f"\n🔍 KEY FINDINGS:")
        for finding in overall_analysis.key_findings:
            print(f"  • {finding}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in overall_analysis.recommendations:
            print(f"  • {rec}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)