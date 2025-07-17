import json
import os
from datetime import datetime
from typing import List, Dict
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.short_term_memory: List[Dict] = []
        self.memory_threshold = 10
        self.memory_dir = "memory_storage"
        os.makedirs(self.memory_dir, exist_ok=True)
        
        logger.info(f"💾 MEMORY MANAGER INITIALIZED\nUser ID: {user_id}\nMemory Threshold: {self.memory_threshold}\nMemory Directory: {self.memory_dir}")
        
    def add_conversation(self, user_message: str, ai_response: str):
        """Add a conversation to memory"""
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "assistant": ai_response
        }
        
        self.short_term_memory.append(conversation)
        
        logger.info(f"💾 CONVERSATION ADDED TO MEMORY\nUser: {self.user_id}\nShort-term Memory Count: {len(self.short_term_memory)}/{self.memory_threshold}\nUser Message Length: {len(user_message)} chars\nAI Response Length: {len(ai_response)} chars")
        
        if len(self.short_term_memory) > self.memory_threshold:
            logger.info(f"📦 MEMORY THRESHOLD EXCEEDED - Moving to long-term storage")
            self._move_to_long_term_memory()
    
    def get_chat_history(self) -> str:
        """Get formatted chat history"""
        history = []
        for conv in self.short_term_memory:
            history.append(f"Human: {conv['user']}")
            history.append(f"Assistant: {conv['assistant']}")
        
        history_str = "\n".join(history)
        logger.info(f"📚 CHAT HISTORY RETRIEVED\nUser: {self.user_id}\nConversations: {len(self.short_term_memory)}\nHistory Length: {len(history_str)} chars")
        
        return history_str
    
    def _move_to_long_term_memory(self):
        """Move oldest conversation to long-term memory"""
        if self.short_term_memory:
            oldest = self.short_term_memory.pop(0)
            date_key = datetime.fromisoformat(oldest["timestamp"]).strftime('%Y-%m-%d')
            
            file_path = os.path.join(self.memory_dir, f"{self.user_id}_{date_key}.json")
            
            logger.info(f"💾 MOVING TO LONG-TERM MEMORY\nUser: {self.user_id}\nDate: {date_key}\nFile: {file_path}")
            
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    memories = json.load(f)
                logger.info(f"📂 EXISTING MEMORY FILE FOUND - {len(memories)} conversations")
            else:
                memories = []
                logger.info("📂 CREATING NEW MEMORY FILE")
            
            memories.append(oldest)
            
            with open(file_path, 'w') as f:
                json.dump(memories, f, indent=2)
                
            logger.info(f"✅ LONG-TERM MEMORY SAVED\nTotal conversations in file: {len(memories)}\nRemaining in short-term: {len(self.short_term_memory)}")
    
    def recall_memory(self, year: int, month: int, day: int) -> str:
        """
        Recall memories from a specific date.
        
        :param year: The year of the conversation (e.g., 2023).
        :param month: The month of the conversation (1-12).
        :param day: The day of the conversation (1-31).
        :return: A string containing the chat history for the given date, or a message if no memories are found.
        """
        logger.info(f"🔍 MEMORY RECALL REQUESTED\nUser: {self.user_id}\nDate: {year}-{month:02d}-{day:02d}")
        
        try:
            date_str = f"{year:04d}-{month:02d}-{day:02d}"
            file_path = os.path.join(self.memory_dir, f"{self.user_id}_{date_str}.json")
            
            logger.info(f"📂 SEARCHING FOR MEMORY FILE: {file_path}")
            
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    memories = json.load(f)
                
                logger.info(f"✅ MEMORY FILE FOUND\nConversations: {len(memories)}")
                
                result = []
                for mem in memories:
                    ts = datetime.fromisoformat(mem['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                    result.append(f"[{ts}]")
                    result.append(f"Human: {mem['user']}")
                    result.append(f"Assistant: {mem['assistant']}")
                
                result_str = "\n".join(result) if result else f"No memories found for {date_str}"
                logger.info(f"📖 MEMORY RECALL COMPLETED\nResult Length: {len(result_str)} chars")
                return result_str
            else:
                logger.warning(f"❌ NO MEMORY FILE FOUND FOR DATE: {date_str}")
                return f"No memory file found for the date: {date_str}"
                
        except (ValueError, TypeError) as e:
            error_msg = f"Error: Invalid date provided. Please provide valid year, month, and day as integers. Details: {e}"
            logger.error(f"❌ INVALID DATE PROVIDED: {e}")
            return error_msg
        except Exception as e:
            error_msg = f"An unexpected error occurred while recalling memory: {e}"
            logger.error(f"❌ MEMORY RECALL ERROR: {e}")
            return error_msg