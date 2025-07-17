import json
import logging
from openai import OpenAI
from django.conf import settings
from pathlib import Path
import time

logger = logging.getLogger(__name__)

class FineTuner:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.base_model = "gpt-4.1-nano-2025-04-14"
        self.training_file_id = None
        self.fine_tuned_model = None
    
    def prepare_training_data(self, conversations, output_file="training_data.jsonl"):
        """
        Prepare conversations data for fine-tuning.
        Format: {"messages": [{"role": "system"}, {"role": "user"}, {"role": "assistant"}]}
        """
        try:
            output_path = Path(settings.BASE_DIR) / "LineBot" / "agent" / "training_data" / output_file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Handle different data formats
            if isinstance(conversations, dict) and "training_examples" in conversations:
                # Format: {"training_examples": [...]}
                conversations = conversations["training_examples"]
            elif isinstance(conversations, list):
                # Format: [...] (direct list)
                conversations = conversations
            else:
                raise ValueError(f"Unexpected data format: {type(conversations)}")
            
            # Convert to OpenAI fine-tuning format
            training_examples = []
            for conv in conversations:
                if all(key in conv for key in ["system", "user", "assistant"]):
                    example = {
                        "messages": [
                            {"role": "system", "content": conv["system"]},
                            {"role": "user", "content": conv["user"]},
                            {"role": "assistant", "content": conv["assistant"]}
                        ]
                    }
                    training_examples.append(example)
            
            # Write JSONL file
            with open(output_path, 'w', encoding='utf-8') as f:
                for example in training_examples:
                    f.write(json.dumps(example, ensure_ascii=False) + '\n')
            
            logger.info(f"Prepared {len(training_examples)} training examples")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            raise
    
    def upload_training_file(self, file_path):
        """Upload training file to OpenAI"""
        try:
            with open(file_path, 'rb') as f:
                response = self.client.files.create(
                    file=f,
                    purpose='fine-tune'
                )
            
            self.training_file_id = response.id
            logger.info(f"Training file uploaded: {self.training_file_id}")
            return self.training_file_id
            
        except Exception as e:
            logger.error(f"Error uploading training file: {e}")
            raise
    
    def create_fine_tuning_job(self):
        """Create and start a fine-tuning job"""
        try:
            if not self.training_file_id:
                raise ValueError("No training file uploaded yet")
            
            response = self.client.fine_tuning.jobs.create(
                training_file=self.training_file_id,
                model=self.base_model,
                hyperparameters={
                    "n_epochs": getattr(settings, 'FINE_TUNING_EPOCHS', 3),
                    "batch_size": getattr(settings, 'FINE_TUNING_BATCH_SIZE', 4)
                }
            )
            
            logger.info(f"Fine-tuning job created: {response.id}")
            return response.id
            
        except Exception as e:
            logger.error(f"Error creating fine-tuning job: {e}")
            raise
    
    def check_fine_tuning_status(self, job_id):
        """Check the status of a fine-tuning job"""
        try:
            job = self.client.fine_tuning.jobs.retrieve(job_id)
            return {
                "status": job.status,
                "fine_tuned_model": job.fine_tuned_model,
                "trained_tokens": getattr(job, 'trained_tokens', None),
                "error": getattr(job, 'error', None)
            }
        except Exception as e:
            logger.error(f"Error checking fine-tuning status: {e}")
            raise
    
    def wait_for_fine_tuning(self, job_id, timeout=3600):
        """Wait for fine-tuning to complete with timeout"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.check_fine_tuning_status(job_id)
            
            if status["status"] in ["succeeded", "failed", "cancelled"]:
                if status["status"] == "succeeded":
                    self.fine_tuned_model = status["fine_tuned_model"]
                    logger.info(f"Fine-tuning completed: {self.fine_tuned_model}")
                else:
                    logger.error(f"Fine-tuning failed: {status['error']}")
                
                return status
            
            time.sleep(30)  # Check every 30 seconds
        
        raise TimeoutError(f"Fine-tuning did not complete within {timeout} seconds")
    
    def list_fine_tuned_models(self):
        """List all fine-tuned models"""
        try:
            response = self.client.fine_tuning.jobs.list()
            return [
                {
                    "job_id": job.id,
                    "model": job.fine_tuned_model,
                    "status": job.status,
                    "created_at": job.created_at
                }
                for job in response.data
                if job.fine_tuned_model
            ]
        except Exception as e:
            logger.error(f"Error listing fine-tuned models: {e}")
            raise
    
    def test_fine_tuned_model(self, model_id, test_prompt):
        """Test a fine-tuned model with a sample prompt"""
        try:
            response = self.client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": "You are an IoT data analysis assistant specializing in environmental monitoring."},
                    {"role": "user", "content": test_prompt}
                ],
                max_tokens=150,
                temperature=0
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error testing fine-tuned model: {e}")
            raise 