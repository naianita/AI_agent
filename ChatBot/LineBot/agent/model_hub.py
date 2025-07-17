from openai import OpenAI
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

class ModelHub:
    def __init__(self):
        # External API client
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.complex_model = settings.COMPLEX_LLM_MODEL  # GPT-4
        self.lightweight_model = settings.LIGHTWEIGHT_LLM_MODEL  # GPT-3.5-turbo
        self.fallback_model = settings.FALLBACK_MODEL  # Fine-tuned GPT-3.5-turbo
        self.use_fallback = False
    
    def complex_llm_call(self, prompt, stop_tokens=None):
        """Call complex LLM for reasoning and planning"""
        try:
            return self._openai_api_call(prompt, stop_tokens, self.complex_model, 2048)
        except Exception as e:
            logger.warning(f"Primary model error: {e}. Attempting fallback...")
            if self.fallback_model and not self.use_fallback:
                self.use_fallback = True  # Prevent recursive fallback
                try:
                    result = self._openai_api_call(prompt, stop_tokens, self.fallback_model, 2048)
                    self.use_fallback = False
                    return result
                except Exception as fallback_error:
                    logger.error(f"Fallback model error: {fallback_error}")
                    self.use_fallback = False
            raise
    
    def lightweight_llm_call(self, prompt):
        """Call lightweight LLM for JSON generation"""
        json_prompt = f"{prompt}\n\nRemember to respond with ONLY valid JSON, no additional text."
        try:
            return self._openai_json_call(json_prompt)
        except Exception as e:
            logger.warning(f"Primary model error: {e}. Attempting fallback...")
            if self.fallback_model and not self.use_fallback:
                self.use_fallback = True
                try:
                    result = self._openai_json_call(json_prompt, model=self.fallback_model)
                    self.use_fallback = False
                    return result
                except Exception as fallback_error:
                    logger.error(f"Fallback model error: {fallback_error}")
                    self.use_fallback = False
            raise
    
    def _openai_api_call(self, prompt, stop_tokens, model, max_tokens):
        """OpenAI API call method"""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant that follows instructions precisely."},
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.AGENT_TEMPERATURE,
                max_tokens=max_tokens,
                stop=stop_tokens if stop_tokens else None
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error calling OpenAI model {model}: {e}")
            raise
    
    def _openai_json_call(self, json_prompt, model=None):
        """OpenAI JSON call method"""
        try:
            response = self.client.chat.completions.create(
                model=model or self.lightweight_model,
                messages=[
                    {"role": "system", "content": "You are a precise AI that outputs only valid JSON without any additional text or formatting."},
                    {"role": "user", "content": json_prompt}
                ],
                temperature=0,
                max_tokens=512,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error calling OpenAI model {model or self.lightweight_model}: {e}")
            raise
    
    def get_model_info(self):
        """Get information about currently loaded models"""
        info = {
            "external_api": {
                "enabled": True,
                "complex_model": self.complex_model,
                "lightweight_model": self.lightweight_model,
                "fallback_model": self.fallback_model,
                "using_fallback": self.use_fallback
            }
        }
        return info