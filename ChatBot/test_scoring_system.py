#!/usr/bin/env python3
"""
Test script to verify the enhanced confidence and reasoning-based scoring system
"""

import os
import sys
import django
from pathlib import Path

# Setup Django environment
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatBot.settings')
django.setup()

from test_accuracy_academic_comprehensive import ComprehensiveAcademicTester

def test_scoring_system():
    """Test the new confidence and reasoning-based scoring system"""
    print("🧪 Testing Enhanced Confidence and Reasoning-Based Scoring System")
    print("=" * 70)
    
    # Create tester instance
    tester = ComprehensiveAcademicTester()
    
    # Test responses with different confidence and reasoning levels
    test_cases = [
        {
            "category": "Reasoning Task",
            "response": "Analysis reveals that CO2 levels are 450ppm, which is 12.5% above the optimal 400ppm threshold. Based on the data, this indicates moderate ventilation inadequacy. Therefore, I recommend increasing air circulation to reduce health risks.",
            "expected_score_range": (0.8, 1.0),
            "description": "High confidence + strong reasoning"
        },
        {
            "category": "Daily Conversation",
            "response": "The capital of France is Paris. This is a well-established geographical fact.",
            "expected_score_range": (0.7, 0.9),
            "description": "High confidence + basic reasoning"
        },
        {
            "category": "Intent Recognition",
            "response": "I understand you're concerned about air quality. Let me check the current sensor readings and analyze the data to assess your environment.",
            "expected_score_range": (0.6, 0.8),
            "description": "Moderate confidence + intent recognition"
        },
        {
            "category": "Memory Test",
            "response": "Referring to our previous discussion about temperature, the current readings show a similar pattern to what we observed yesterday.",
            "expected_score_range": (0.7, 0.9),
            "description": "Good contextual reasoning"
        },
        {
            "category": "Refusal Test",
            "response": "I don't have the capability to play music. However, I can help you analyze your indoor environment and air quality data.",
            "expected_score_range": (0.8, 1.0),
            "description": "Proper refusal with alternative"
        },
        {
            "category": "Reasoning Task",
            "response": "I think maybe the levels might be high but I'm not sure what that means.",
            "expected_score_range": (0.1, 0.4),
            "description": "Low confidence + weak reasoning"
        }
    ]
    
    print(f"\n🔍 Testing {len(test_cases)} response scenarios:")
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        category = test_case["category"]
        response = test_case["response"]
        expected_min, expected_max = test_case["expected_score_range"]
        description = test_case["description"]
        
        # Calculate scores
        confidence_score = tester._evaluate_confidence_score(response)
        reasoning_score = tester._evaluate_reasoning_quality(response, category)
        final_score = tester._score_response(category, {}, response)
        
        # Check if score is in expected range
        in_range = expected_min <= final_score <= expected_max
        status = "✅ PASS" if in_range else "❌ FAIL"
        
        if in_range:
            passed_tests += 1
        
        print(f"\n{status} Test {i}: {description}")
        print(f"   Category: {category}")
        print(f"   Response: \"{response[:60]}{'...' if len(response) > 60 else ''}\"")
        print(f"   Scores: Final={final_score:.3f} (C:{confidence_score:.3f}, R:{reasoning_score:.3f})")
        print(f"   Expected: {expected_min:.1f}-{expected_max:.1f}, Got: {final_score:.3f}")
        
        if not in_range:
            print(f"   ⚠️  Score outside expected range!")
    
    # Summary
    accuracy = passed_tests / total_tests
    print(f"\n{'='*70}")
    print(f"🎯 SCORING SYSTEM TEST RESULTS")
    print(f"{'='*70}")
    print(f"Passed: {passed_tests}/{total_tests} ({accuracy:.1%})")
    
    if accuracy >= 0.8:
        print("✅ Excellent! Scoring system working as expected.")
    elif accuracy >= 0.6:
        print("⚠️  Good! Minor calibration may be needed.")
    else:
        print("❌ Poor! Scoring system needs adjustment.")
    
    return accuracy >= 0.8

def test_category_weighting():
    """Test that different categories use appropriate weighting"""
    print(f"\n🏗️  Testing Category-Specific Weighting")
    print("=" * 50)
    
    tester = ComprehensiveAcademicTester()
    
    # Same response, different categories - should score differently
    test_response = "Based on analysis, the data shows clear patterns with statistical significance."
    
    categories = ["Daily Conversation", "Intent Recognition", "Reasoning Task", 
                 "Multi-task Test", "Memory Test", "Refusal Test"]
    
    scores = {}
    for category in categories:
        score = tester._score_response(category, {}, test_response)
        scores[category] = score
        print(f"{category:20}: {score:.3f}")
    
    # Reasoning Task should score highest due to 45% reasoning weight
    reasoning_score = scores["Reasoning Task"]
    other_scores = [scores[cat] for cat in categories if cat != "Reasoning Task"]
    
    if reasoning_score >= max(other_scores):
        print("✅ Category weighting working correctly")
        return True
    else:
        print("❌ Category weighting needs adjustment")
        return False

def main():
    """Main test function"""
    print("🎓 Enhanced Confidence and Reasoning Scoring System Validation")
    print("=" * 80)
    
    # Test scoring accuracy
    scoring_test_passed = test_scoring_system()
    
    # Test category weighting
    weighting_test_passed = test_category_weighting()
    
    overall_success = scoring_test_passed and weighting_test_passed
    
    print(f"\n🏆 OVERALL TEST RESULT: {'✅ PASSED' if overall_success else '❌ FAILED'}")
    
    if overall_success:
        print("🎯 The enhanced scoring system is ready for academic testing!")
        print("📊 Run test_accuracy_academic_comprehensive.py to see it in action.")
    else:
        print("⚠️  Scoring system needs calibration before use.")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)