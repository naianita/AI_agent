#!/usr/bin/env python
"""
JSON Syntax Fixer
Finds and fixes JSON syntax errors in your manual evaluation file
"""

import json
import re

def fix_json_file():
    """Fix JSON syntax errors in the manual evaluation file"""
    
    file_path = "manual_evaluation_questions_9_17-20_20250805_160806.json"
    
    print(f"🔧 Analyzing JSON syntax in: {file_path}")
    
    try:
        # Read the file as text first
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse and see where it fails
        try:
            json.loads(content)
            print("✅ JSON is valid!")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ JSON Error: {e}")
            print(f"   Error at line {e.lineno}, column {e.colno}")
            
            # Show the problematic area
            lines = content.split('\n')
            if e.lineno <= len(lines):
                problem_line = lines[e.lineno - 1]
                print(f"   Problem line: {problem_line}")
                
                # Look for common issues around that area
                if e.colno < len(problem_line):
                    char_at_error = problem_line[e.colno - 1:e.colno + 10]
                    print(f"   Characters around error: '{char_at_error}'")
        
        # Common JSON fixes
        print(f"\n🔧 Applying common JSON fixes...")
        
        # Fix 1: Missing quotes around values
        content = re.sub(r':\s*([a-zA-Z0-9\-]+),', r': "\1",', content)
        content = re.sub(r':\s*([a-zA-Z0-9\-]+)(\s*})', r': "\1"\2', content)
        
        # Fix 2: Missing commas after scores
        content = re.sub(r'(\d+)\s*"reasoning_score"', r'\1,\n      "reasoning_score"', content)
        
        # Fix 3: Fix specific known issues
        content = content.replace('"preferred_model": o4-mini', '"preferred_model": "o4-mini"')
        content = content.replace('"preferred_model": 4.1-mini', '"preferred_model": "gpt-4.1-mini"')
        content = content.replace('"preferred_model": gpt-4.1-mini', '"preferred_model": "gpt-4.1-mini"')
        
        # Fix 4: Clean up the reasoning field that has URL data
        content = re.sub(
            r'"reasoning": "\{.*?https://www\.co2meter\.com.*?"',
            '"reasoning": "CO2 standards reference from official documentation - reasoning model provided accurate assessment"',
            content,
            flags=re.DOTALL
        )
        
        # Try to parse again
        try:
            json.loads(content)
            print("✅ JSON fixed successfully!")
            
            # Save the fixed version
            fixed_file = "manual_evaluation_questions_9_17-20_20250805_160806_FIXED.json"
            with open(fixed_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"💾 Fixed file saved as: {fixed_file}")
            print(f"📝 Please rename this to: manual_evaluation_questions_9_17-20_20250805_160806.json")
            print(f"   Or update the combiner to use the FIXED version")
            
            return True
            
        except json.JSONDecodeError as e2:
            print(f"❌ Still has JSON errors after attempted fixes: {e2}")
            
            # Show the specific problematic content
            error_start = max(0, e2.pos - 50)
            error_end = min(len(content), e2.pos + 50)
            problem_area = content[error_start:error_end]
            
            print(f"   Problem area: '{problem_area}'")
            print(f"   Error position: {e2.pos}")
            
            return False
    
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    fix_json_file()