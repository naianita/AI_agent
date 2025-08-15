#!/usr/bin/env python
"""
Manual Override Combiner
Replaces AI evaluation results for Q9,17,18,19,20 with your more accurate manual evaluation
"""

import json
import os
from datetime import datetime
import statistics
from typing import Dict, List, Any

class ManualOverrideCombiner:
    """Combines AI evaluation with manual override for specific questions"""
    
    def __init__(self):
        self.manual_override_questions = [9, 17, 18, 19, 20]
        self.ai_evaluation_questions = [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16]
    
    def load_ai_evaluation_results(self) -> Dict:
        """Load AI evaluation results from fair evaluation system"""
        
        # Look for the summary table file
        summary_files = [f for f in os.listdir('.') if f.startswith('fair_evaluation_summary_table_') and f.endswith('.json')]
        
        if not summary_files:
            print(f"❌ No fair evaluation summary found!")
            print(f"Please run: python fair_evaluation_system_updated.py")
            return None
        
        # Use the most recent file
        summary_file = max(summary_files, key=lambda f: os.path.getctime(f))
        print(f"📊 Loading AI evaluation results: {summary_file}")
        
        with open(summary_file, 'r', encoding='utf-8') as f:
            ai_data = json.load(f)
        
        # Process AI results
        ai_results = {}
        for question_data in ai_data['question_by_question_scores']:
            question_id = question_data['question_id']
            
            # Only keep questions that aren't manually overridden
            if question_id not in self.manual_override_questions:
                ai_results[question_id] = {
                    'question_id': question_id,
                    'category': question_data['category'],
                    'question': question_data['question'],
                    'winner': question_data['winner'],
                    'confidence': question_data['confidence'],
                    'gpt_total_score': question_data['total_scores']['gpt_4_1_mini'],
                    'reasoning_total_score': question_data['total_scores']['o4_mini'],
                    'gpt_avg_score': question_data['total_scores']['gpt_4_1_mini'] / 5,
                    'reasoning_avg_score': question_data['total_scores']['o4_mini'] / 5,
                    'dimension_scores': question_data['dimension_scores'],
                    'evaluation_method': 'ai_evaluation'
                }
        
        print(f"✅ Loaded {len(ai_results)} AI evaluation results (excluding manual override questions)")
        return ai_results
    
    def load_manual_evaluation(self) -> Dict:
        """Load your manual evaluation for questions 9, 17-20"""
        
        manual_file = "manual_evaluation_questions_9_17-20_20250805_160806.json"
        if not os.path.exists(manual_file):
            print(f"❌ Manual evaluation file not found: {manual_file}")
            return None
        
        print(f"📝 Loading manual evaluation: {manual_file}")
        
        with open(manual_file, 'r', encoding='utf-8') as f:
            manual_data = json.load(f)
        
        # Process manual results
        manual_results = {}
        for item in manual_data['evaluation_items']:
            question_id = item['question_id']
            
            # Calculate scores
            dimensions = item['evaluation_dimensions']
            gpt_scores = [dim['gpt_score'] for dim in dimensions.values()]
            reasoning_scores = [dim['reasoning_score'] for dim in dimensions.values()]
            
            manual_results[question_id] = {
                'question_id': question_id,
                'category': item['category'],
                'question': item['question'],
                'winner': item['overall_assessment']['preferred_model'],
                'confidence': item['overall_assessment']['confidence'],
                'gpt_total_score': sum(gpt_scores),
                'reasoning_total_score': sum(reasoning_scores),
                'gpt_avg_score': statistics.mean(gpt_scores),
                'reasoning_avg_score': statistics.mean(reasoning_scores),
                'dimension_scores': {
                    'accuracy': {'gpt_4_1_mini': dimensions['accuracy']['gpt_score'], 'o4_mini': dimensions['accuracy']['reasoning_score']},
                    'completeness': {'gpt_4_1_mini': dimensions['completeness']['gpt_score'], 'o4_mini': dimensions['completeness']['reasoning_score']},
                    'task_appropriateness': {'gpt_4_1_mini': dimensions['task_appropriateness']['gpt_score'], 'o4_mini': dimensions['task_appropriateness']['reasoning_score']},
                    'transparency': {'gpt_4_1_mini': dimensions['transparency']['gpt_score'], 'o4_mini': dimensions['transparency']['reasoning_score']},
                    'practical_value': {'gpt_4_1_mini': dimensions['practical_value']['gpt_score'], 'o4_mini': dimensions['practical_value']['reasoning_score']}
                },
                'evaluation_method': 'manual_override'
            }
        
        print(f"✅ Loaded {len(manual_results)} manual evaluation results")
        return manual_results
    
    def combine_with_manual_override(self, ai_results: Dict, manual_results: Dict) -> Dict:
        """Combine AI results with manual override"""
        
        print(f"🔄 Combining results with manual override...")
        print(f"   AI evaluation questions: {sorted(ai_results.keys())}")
        print(f"   Manual override questions: {sorted(manual_results.keys())}")
        
        # Combine all results (manual overrides AI for specified questions)
        all_results = {}
        
        # Add AI results
        all_results.update(ai_results)
        
        # Override with manual results (this replaces AI scores for Q9,17,18,19,20)
        all_results.update(manual_results)
        
        # Calculate comprehensive statistics
        all_gpt_scores = [data['gpt_avg_score'] for data in all_results.values()]
        all_reasoning_scores = [data['reasoning_avg_score'] for data in all_results.values()]
        
        # Count preferences
        preferences = {'gpt-4.1-mini': 0, 'o4-mini': 0, 'tie': 0}
        for data in all_results.values():
            pref = data['winner']
            if pref in preferences:
                preferences[pref] += 1
        
        # Category breakdown
        categories = {}
        for question_id, data in all_results.items():
            category = data['category']
            if category not in categories:
                categories[category] = {
                    'questions': [],
                    'gpt_scores': [],
                    'reasoning_scores': [],
                    'preferences': {'gpt-4.1-mini': 0, 'o4-mini': 0, 'tie': 0},
                    'evaluation_methods': []
                }
            
            categories[category]['questions'].append(question_id)
            categories[category]['gpt_scores'].append(data['gpt_avg_score'])
            categories[category]['reasoning_scores'].append(data['reasoning_avg_score'])
            categories[category]['preferences'][data['winner']] += 1
            categories[category]['evaluation_methods'].append(data['evaluation_method'])
        
        # Generate final combined report
        combined_report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'methodology': 'AI Evaluation with Manual Override for Q9,17,18,19,20',
            'evaluation_breakdown': {
                'ai_evaluated': sorted(ai_results.keys()),
                'manual_override': sorted(manual_results.keys()),
                'total_questions': len(all_results)
            },
            'overall_statistics': {
                'gpt_4_1_mini_avg': round(statistics.mean(all_gpt_scores), 2),
                'o4_mini_avg': round(statistics.mean(all_reasoning_scores), 2),
                'score_difference': round(statistics.mean(all_reasoning_scores) - statistics.mean(all_gpt_scores), 2),
                'preferences': preferences,
                'preference_percentages': {
                    'gpt_4_1_mini': f"{preferences['gpt-4.1-mini']/20*100:.1f}%",
                    'o4_mini': f"{preferences['o4-mini']/20*100:.1f}%",
                    'tie': f"{preferences['tie']/20*100:.1f}%"
                }
            },
            'category_breakdown': {},
            'question_by_question_results': all_results
        }
        
        # Add category analysis
        for category, data in categories.items():
            gpt_avg = statistics.mean(data['gpt_scores'])
            reasoning_avg = statistics.mean(data['reasoning_scores'])
            
            combined_report['category_breakdown'][category] = {
                'questions': sorted(data['questions']),
                'question_count': len(data['questions']),
                'gpt_avg_score': round(gpt_avg, 2),
                'reasoning_avg_score': round(reasoning_avg, 2),
                'score_difference': round(reasoning_avg - gpt_avg, 2),
                'preferences': data['preferences'],
                'reasoning_advantage': reasoning_avg > gpt_avg,
                'evaluation_mix': list(set(data['evaluation_methods']))
            }
        
        return combined_report
    
    def save_final_results(self, combined_report: Dict) -> tuple:
        """Save the final combined results"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save complete results
        results_file = f"final_evaluation_results_manual_override_{timestamp}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(combined_report, f, indent=2, ensure_ascii=False)
        
        # Generate summary report
        report_file = f"final_evaluation_summary_manual_override_{timestamp}.md"
        
        stats = combined_report['overall_statistics']
        
        report = f"""# Final Fair Model Evaluation Report (Manual Override)
Generated: {combined_report['timestamp']}

## Methodology
- **AI Evaluation**: Questions 1-8, 10-16 (15 questions) - Consistent bias-aware assessment
- **Manual Override**: Questions 9, 17-20 (5 questions) - Your expert domain knowledge
- **Result**: Most accurate evaluation combining AI consistency with human expertise

## Overall Results

### Average Scores (1-10 scale)
- **GPT-4.1-mini**: {stats['gpt_4_1_mini_avg']}/10
- **O4-mini**: {stats['o4_mini_avg']}/10  
- **Score Difference**: {stats['score_difference']:+.2f} (positive = reasoning model advantage)

### Model Preferences (All 20 Questions)
- **GPT-4.1-mini**: {stats['preference_percentages']['gpt_4_1_mini']} ({stats['preferences']['gpt-4.1-mini']}/20 questions)
- **O4-mini**: {stats['preference_percentages']['o4_mini']} ({stats['preferences']['o4-mini']}/20 questions)
- **Tie**: {stats['preference_percentages']['tie']} ({stats['preferences']['tie']}/20 questions)

## Category Analysis (With Manual Override)

"""
        
        for category, details in combined_report['category_breakdown'].items():
            questions_str = ", ".join(map(str, details['questions']))
            eval_methods = ", ".join(details['evaluation_methods'])  # Changed from 'evaluation_mix' to 'evaluation_methods'
            
            report += f"""### {category} (Questions: {questions_str})
- **Evaluation Method**: {eval_methods}
- **Question Count**: {details['question_count']}
- **GPT-4.1-mini Average**: {details['gpt_avg_score']}/10
- **O4-mini Average**: {details['reasoning_avg_score']}/10
- **Score Difference**: {details['score_difference']:+.2f}
- **Winner Distribution**: GPT({details['preferences']['gpt-4.1-mini']}) vs O4({details['preferences']['o4-mini']}) vs Tie({details['preferences']['tie']})
- **Analysis**: {"Reasoning model advantage" if details['reasoning_advantage'] else "GPT model advantage or comparable"}

"""
        
        # Add comprehensive insights
        report += f"""## Key Insights (Manual Override Applied)

### Accuracy Improvements
- **Questions 9, 17-20**: Manual evaluation provided more accurate assessment based on:
  - Actual data verification (Q9, Q19, Q20)
  - Domain expertise in environmental monitoring
  - Understanding of model behavior with real IoT data

### Model Performance Patterns
"""
        
        if stats['score_difference'] > 1:
            report += "- 📈 **Strong O4-mini advantage** across evaluation with manual corrections\n"
        elif stats['score_difference'] > 0.3:
            report += "- 📊 **Moderate O4-mini advantage** with manual accuracy improvements\n"
        else:
            report += "- ⚖️ **Balanced performance** with manual corrections applied\n"
        
        if stats['preferences']['o4-mini'] > 15:
            report += f"- 🎯 **Clear O4-mini preference** in {stats['preferences']['o4-mini']}/20 evaluations (including manual corrections)\n"
        
        report += f"""
### Evaluation Quality
- **AI Evaluation Strength**: Consistent methodology across 15 questions
- **Manual Override Value**: Expert knowledge for data-dependent and complex reasoning tasks
- **Combined Result**: Most accurate assessment possible

## Final Recommendations

Based on the corrected evaluation with manual override:
"""
        
        if stats['preferences']['o4-mini'] > 15:
            report += """- **Primary Recommendation**: Use O4-mini as main model for this IoT environmental monitoring application
- **Reasoning**: Superior performance in complex reasoning, data analysis, and transparency
- **Use GPT-4.1-mini for**: Quick direct answers and simple conversational interactions
- **Key Advantage**: O4-mini's visible reasoning process valuable for data verification and complex environmental assessments
"""
        else:
            report += """- **Balanced Approach**: Both models have specific strengths
- **Use O4-mini for**: Complex reasoning, multi-step analysis, data interpretation
- **Use GPT-4.1-mini for**: Direct answers, simple questions, efficiency-focused tasks
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return results_file, report_file
    
    def run_manual_override_combination(self):
        """Run the manual override combination"""
        
        print("🎯 Manual Override Results Combiner")
        print("AI Evaluation + Manual Override → Most Accurate Results")
        print("=" * 60)
        
        # Step 1: Load AI evaluation results
        ai_results = self.load_ai_evaluation_results()
        if not ai_results:
            return False
        
        # Step 2: Load manual evaluation
        manual_results = self.load_manual_evaluation()
        if not manual_results:
            return False
        
        # Step 3: Combine with manual override
        combined_report = self.combine_with_manual_override(ai_results, manual_results)
        
        # Step 4: Save final results
        results_file, report_file = self.save_final_results(combined_report)
        
        # Step 5: Display summary
        print(f"\n🎉 Final evaluation with manual override complete!")
        print(f"📊 Files generated:")
        print(f"   Complete results: {results_file}")
        print(f"   Summary report: {report_file}")
        
        # Show the override effect
        stats = combined_report['overall_statistics']
        print(f"\n📈 Final Results (With Manual Override):")
        print(f"  Average Scores: GPT({stats['gpt_4_1_mini_avg']}) vs O4({stats['o4_mini_avg']})")
        print(f"  Model Preferences: GPT({stats['preferences']['gpt-4.1-mini']}) vs O4({stats['preferences']['o4-mini']}) vs Tie({stats['preferences']['tie']})")
        print(f"  Score Difference: {stats['score_difference']:+.2f}")
        
        print(f"\n✨ Override Summary:")
        print(f"  📊 AI Evaluation: Questions {sorted(ai_results.keys())} ({len(ai_results)} questions)")
        print(f"  📝 Manual Override: Questions {self.manual_override_questions} (5 questions)")
        print(f"  🎯 Result: Most accurate evaluation combining AI consistency with human expertise")
        
        return True
    
    def load_manual_evaluation(self) -> Dict:
        """Load manual evaluation data"""
        
        manual_file = "manual_evaluation_questions_9_17-20_20250805_160806.json"
        print(f"📝 Loading manual evaluation: {manual_file}")
        
        with open(manual_file, 'r', encoding='utf-8') as f:
            manual_data = json.load(f)
        
        # Process manual results  
        manual_results = {}
        for item in manual_data['evaluation_items']:
            question_id = item['question_id']
            
            # Calculate scores
            dimensions = item['evaluation_dimensions']
            gpt_scores = [dim['gpt_score'] for dim in dimensions.values()]
            reasoning_scores = [dim['reasoning_score'] for dim in dimensions.values()]
            
            # Convert dimension names to match AI evaluation format
            dimension_scores = {}
            for dim_name, dim_data in dimensions.items():
                # Capitalize first letter to match AI format
                formatted_name = dim_name.replace('_', ' ').title()
                if formatted_name == 'Task Appropriateness':
                    formatted_name = 'Task Appropriateness'
                elif formatted_name == 'Practical Value':
                    formatted_name = 'Practical Value'
                
                dimension_scores[formatted_name] = {
                    'gpt_4_1_mini': dim_data['gpt_score'],
                    'o4_mini': dim_data['reasoning_score']
                }
            
            manual_results[question_id] = {
                'question_id': question_id,
                'category': item['category'],
                'question': item['question'],
                'winner': item['overall_assessment']['preferred_model'],
                'confidence': item['overall_assessment']['confidence'],
                'gpt_total_score': sum(gpt_scores),
                'reasoning_total_score': sum(reasoning_scores),
                'gpt_avg_score': statistics.mean(gpt_scores),
                'reasoning_avg_score': statistics.mean(reasoning_scores),
                'dimension_scores': dimension_scores,
                'evaluation_method': 'manual_override'
            }
        
        return manual_results
    
    def combine_with_manual_override(self, ai_results: Dict, manual_results: Dict) -> Dict:
        """Combine AI and manual results with manual taking priority"""
        
        # Start with AI results
        all_results = ai_results.copy()
        
        # Override with manual results for Q9,17,18,19,20
        for question_id, manual_data in manual_results.items():
            all_results[question_id] = manual_data
            print(f"   ✅ Overrode Q{question_id} with manual evaluation")
        
        # Calculate final statistics
        all_gpt_scores = [data['gpt_avg_score'] for data in all_results.values()]
        all_reasoning_scores = [data['reasoning_avg_score'] for data in all_results.values()]
        
        # Count preferences  
        preferences = {'gpt-4.1-mini': 0, 'o4-mini': 0, 'tie': 0}
        for data in all_results.values():
            pref = data['winner']
            if pref in preferences:
                preferences[pref] += 1
        
        # Category breakdown
        categories = {}
        for question_id, data in all_results.items():
            category = data['category']
            if category not in categories:
                categories[category] = {
                    'questions': [],
                    'gpt_scores': [],
                    'reasoning_scores': [],
                    'preferences': {'gpt-4.1-mini': 0, 'o4-mini': 0, 'tie': 0},
                    'evaluation_methods': []
                }
            
            categories[category]['questions'].append(question_id)
            categories[category]['gpt_scores'].append(data['gpt_avg_score'])
            categories[category]['reasoning_scores'].append(data['reasoning_avg_score'])
            categories[category]['preferences'][data['winner']] += 1
            categories[category]['evaluation_methods'].append(data['evaluation_method'])
        
        # Generate final report
        combined_report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'methodology': 'AI Evaluation with Manual Override (Most Accurate)',
            'evaluation_breakdown': {
                'ai_evaluated': sorted([k for k, v in all_results.items() if v['evaluation_method'] == 'ai_evaluation']),
                'manual_override': sorted([k for k, v in all_results.items() if v['evaluation_method'] == 'manual_override']),
                'total_questions': len(all_results)
            },
            'overall_statistics': {
                'gpt_4_1_mini_avg': round(statistics.mean(all_gpt_scores), 2),
                'o4_mini_avg': round(statistics.mean(all_reasoning_scores), 2),
                'score_difference': round(statistics.mean(all_reasoning_scores) - statistics.mean(all_gpt_scores), 2),
                'preferences': preferences,
                'preference_percentages': {
                    'gpt_4_1_mini': f"{preferences['gpt-4.1-mini']/20*100:.1f}%",
                    'o4_mini': f"{preferences['o4-mini']/20*100:.1f}%",
                    'tie': f"{preferences['tie']/20*100:.1f}%"
                }
            },
            'category_breakdown': {},
            'question_by_question_results': all_results
        }
        
        # Add category analysis
        for category, data in categories.items():
            gpt_avg = statistics.mean(data['gpt_scores'])
            reasoning_avg = statistics.mean(data['reasoning_scores'])
            
            combined_report['category_breakdown'][category] = {
                'questions': sorted(data['questions']),
                'question_count': len(data['questions']),
                'gpt_avg_score': round(gpt_avg, 2),
                'reasoning_avg_score': round(reasoning_avg, 2),
                'score_difference': round(reasoning_avg - gpt_avg, 2),
                'preferences': data['preferences'],
                'reasoning_advantage': reasoning_avg > gpt_avg,
                'evaluation_methods': list(set(data['evaluation_methods']))
            }
        
        return combined_report

def main():
    """Main function"""
    
    try:
        combiner = ManualOverrideCombiner()
        success = combiner.run_manual_override_combination()
        return success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)