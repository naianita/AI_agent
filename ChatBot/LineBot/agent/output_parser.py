import re
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class OutputParser:
    def __init__(self):
        self.thought_pattern = r"Thought: (.*?)(?=\n[A-Z]|$)"
        self.action_pattern = r"Action: (.*?)(?=\n[A-Z]|$)"
        self.final_answer_pattern = r"Final Answer: (.*?)(?=\n[A-Z]|$)"

    def parse(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Parse the model's response into structured format.
        Handles three types of responses:
        1. Thought only
        2. Thought + Action
        3. Final Answer
        """
        try:
            # Clean the text
            text = text.strip()
            
            # Try to find a final answer first
            final_answer_match = re.search(self.final_answer_pattern, text, re.DOTALL)
            if final_answer_match:
                return {
                    "type": "final_answer",
                    "content": final_answer_match.group(1).strip()
                }

            # Look for thought
            thought_match = re.search(self.thought_pattern, text, re.DOTALL)
            thought = thought_match.group(1).strip() if thought_match else None

            # Look for action
            action_match = re.search(self.action_pattern, text, re.DOTALL)
            if action_match:
                try:
                    action_json = json.loads(action_match.group(1).strip())
                    return {
                        "type": "action",
                        "thought": thought,
                        "tool": action_json.get("tool"),
                        "parameters": action_json.get("parameters", {})
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse action JSON: {e}")
                    return None

            # If we only found a thought
            if thought:
                return {
                    "type": "thought",
                    "content": thought
                }

            logger.warning(f"Could not parse response: {text[:100]}...")
            return None

        except Exception as e:
            logger.error(f"Error parsing output: {str(e)}")
            return None

    def format_tool_response(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Format a tool call into JSON string"""
        tool_call = {
            "tool": tool_name,
            "parameters": parameters
        }
        return json.dumps(tool_call, indent=2)

    def format_observation(self, result: Any) -> str:
        """Format tool result into observation string"""
        if isinstance(result, (dict, list)):
            return json.dumps(result, indent=2)
        return str(result)

    def extract_task_components(self, text: str) -> Dict[str, Any]:
        """
        Extract components from a sequential task description:
        - Goal
        - Steps
        - Success criteria
        """
        components = {
            "goal": "",
            "steps": [],
            "success_criteria": ""
        }
        
        # Try to find goal
        goal_match = re.search(r"Goal:?\s*(.*?)(?=\n|$)", text, re.IGNORECASE)
        if goal_match:
            components["goal"] = goal_match.group(1).strip()
        
        # Try to find steps
        steps_matches = re.findall(r"\d+\.\s*(.*?)(?=\n\d+\.|\n\n|$)", text)
        if steps_matches:
            components["steps"] = [step.strip() for step in steps_matches]
        
        # Try to find success criteria
        criteria_match = re.search(r"Success Criteria:?\s*(.*?)(?=\n|$)", text, re.IGNORECASE)
        if criteria_match:
            components["success_criteria"] = criteria_match.group(1).strip()
        
        return components

    def extract_navigation_components(self, text: str) -> Dict[str, Any]:
        """
        Extract components from a navigation request:
        - Current view
        - Target view
        - Actions needed
        """
        components = {
            "current_view": "",
            "target_view": "",
            "actions": []
        }
        
        # Try to find current view
        current_match = re.search(r"Current(?:\s+View)?:?\s*(.*?)(?=\n|$)", text, re.IGNORECASE)
        if current_match:
            components["current_view"] = current_match.group(1).strip()
        
        # Try to find target view
        target_match = re.search(r"Target(?:\s+View)?:?\s*(.*?)(?=\n|$)", text, re.IGNORECASE)
        if target_match:
            components["target_view"] = target_match.group(1).strip()
        
        # Try to find actions
        actions_matches = re.findall(r"\d+\.\s*(.*?)(?=\n\d+\.|\n\n|$)", text)
        if actions_matches:
            components["actions"] = [action.strip() for action in actions_matches]
        
        return components