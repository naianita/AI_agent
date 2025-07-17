from typing import Dict, List, Any, Optional
import logging
from .model_hub import ModelHub
from .tool_manager import ToolManager
from .prompt_template import PromptTemplate
from .output_parser import OutputParser

logger = logging.getLogger(__name__)

class ReActAgent:
    def __init__(self, model_hub: ModelHub, tool_manager: ToolManager):
        self.model_hub = model_hub
        self.tool_manager = tool_manager
        self.prompt_template = PromptTemplate()
        self.output_parser = OutputParser()
        self.max_iterations = 5
    def process_message(self, message: str)  -> str:
        result = self.solve(message)
        return result["final_answer"]
    def _log_thought_action(self, step: str, content: str):
        """Log agent's thoughts and actions for monitoring"""
        logger.info(f"[{step}] {content}")

    def solve(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main ReAct loop implementing the reasoning-action cycle:
        1. Thought: Analyze the current situation
        2. Action: Decide and execute an action
        3. Observation: Process the action's result
        4. Repeat until reaching a final answer
        """
        iteration = 0
        conversation_history = []
        final_answer = None

        while iteration < self.max_iterations and not final_answer:
            # Generate prompt with current context
            chat_history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
            prompt = self.prompt_template.get_complex_prompt(
                user_input=user_input,
                tools_description=self.tool_manager.get_tools_description(),
                chat_history=chat_history_str
            )

            # Get model's response
            response = self.model_hub.complex_llm_call(prompt)
            parsed_response = self.output_parser.parse(response)

            if not parsed_response:
                logger.error(f"Failed to parse model response: {response}")
                break

            # Process based on response type
            if parsed_response["type"] == "thought":
                self._log_thought_action("Thought", parsed_response["content"])
                conversation_history.append({"role": "assistant", "content": f"Thought: {parsed_response['content']}"})

            elif parsed_response["type"] == "action":
                self._log_thought_action("Action", f"Using tool: {parsed_response['tool']}")
                
                # Execute tool and get observation
                try:
                    tool_result = self.tool_manager.execute_tool(
                        tool_name=parsed_response["tool"],
                        parameters=parsed_response["parameters"]
                    )
                    observation = f"Observation: {tool_result}"
                    self._log_thought_action("Observation", tool_result)
                    conversation_history.append({"role": "system", "content": observation})
                
                except Exception as e:
                    error_msg = f"Error executing tool: {str(e)}"
                    logger.error(error_msg)
                    observation = f"Observation: {error_msg}"
                    conversation_history.append({"role": "system", "content": observation})

            elif parsed_response["type"] == "final_answer":
                final_answer = parsed_response["content"]
                self._log_thought_action("Final Answer", final_answer)
                conversation_history.append({"role": "assistant", "content": f"Final Answer: {final_answer}"})

            iteration += 1

        if not final_answer:
            final_answer = "I apologize, but I was unable to complete the task within the allowed iterations."

        return {
            "final_answer": final_answer,
            "conversation_history": conversation_history,
            "iterations": iteration
        }

    def analyze_iot_data(self, query: str, time_range: Optional[str] = "24h") -> Dict[str, Any]:
        """
        Specialized method for IoT data analysis using ReAct:
        1. Thought: Understand what data and analysis is needed
        2. Action: Fetch and process relevant IoT data
        3. Observation: Analyze the results
        4. Reasoning: Draw conclusions from the analysis
        """
        context = {
            "time_range": time_range,
            "data_types": ["temperature", "humidity", "co2", "tvoc"],
            "analysis_mode": True
        }
        
        return self.solve(query, context)

    def optimize_environment(self, target_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        ReAct-based environmental optimization:
        1. Thought: Analyze current vs target conditions
        2. Action: Check relevant sensors
        3. Observation: Compare with targets
        4. Action: Suggest or implement adjustments
        5. Reasoning: Verify improvements
        """
        query = f"Optimize environment to meet conditions: {str(target_conditions)}"
        context = {
            "target_conditions": target_conditions,
            "optimization_mode": True
        }
        
        return self.solve(query, context)

    def handle_sequential_task(self, task_description: str, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Handle multi-step tasks using ReAct:
        1. Thought: Plan task sequence
        2. Action: Execute each step
        3. Observation: Monitor progress
        4. Reasoning: Adjust plan if needed
        """
        context = {
            "task_type": "sequential",
            "steps": steps
        }
        
        return self.solve(task_description, context)

    def navigate_interface(self, navigation_request: str) -> Dict[str, Any]:
        """
        Handle interface navigation using ReAct:
        1. Thought: Understand navigation goal
        2. Action: Identify current and target views
        3. Observation: Check available paths
        4. Reasoning: Choose optimal navigation
        """
        context = {
            "task_type": "navigation",
            "interface_mode": True
        }
        
        return self.solve(navigation_request, context)