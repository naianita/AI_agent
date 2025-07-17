from django.core.management.base import BaseCommand
from LineBot.agent.fine_tuner import FineTuner
import json
import logging
import time
from django.conf import settings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fine-tune GPT-4.1-nano model as a fallback with enhanced monitoring'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data-file',
            type=str,
            help='Path to training data file (JSON format)',
            required=True
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            help='Wait for fine-tuning to complete'
        )
        parser.add_argument(
            '--cost-estimate-only',
            action='store_true',
            help='Only estimate costs without starting fine-tuning'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting OpenAI Fine-tuning Process for IoT Agent')
        )
        
        try:
            # Load training data
            self.stdout.write('📥 Loading training data...')
            with open(options['data_file'], 'r', encoding='utf-8') as f:
                training_data = json.load(f)

            # Handle different data formats
            if isinstance(training_data, dict) and "training_examples" in training_data:
                examples = training_data["training_examples"]
            elif isinstance(training_data, list):
                examples = training_data
            else:
                raise ValueError("Invalid training data format")

            self.stdout.write(
                self.style.SUCCESS(f'✅ Loaded {len(examples)} training examples')
            )

            # Estimate costs
            avg_tokens = 300  # Estimated tokens per example
            total_tokens = len(examples) * avg_tokens
            estimated_cost = self._calculate_fine_tuning_cost(total_tokens)
            
            self.stdout.write(
                self.style.WARNING(f'\n💰 Cost Estimation:')
            )
            self.stdout.write(f'   Training examples: {len(examples)}')
            self.stdout.write(f'   Estimated tokens: {total_tokens:,}')
            self.stdout.write(f'   Estimated cost: ${estimated_cost:.2f}')
            
            if options['cost_estimate_only']:
                self.stdout.write(
                    self.style.SUCCESS('\n📊 Cost estimation complete. Use --wait to proceed with training.')
                )
                return

            # Confirm before proceeding
            if not self._confirm_proceed(estimated_cost):
                self.stdout.write(self.style.ERROR('❌ Fine-tuning cancelled by user'))
                return

            # Initialize fine-tuner
            self.stdout.write('\n🔧 Initializing fine-tuner...')
            fine_tuner = FineTuner()

            # Prepare and upload training data
            self.stdout.write('📤 Preparing and uploading training data...')
            training_file = fine_tuner.prepare_training_data(examples)
            self.stdout.write(self.style.SUCCESS(f'✅ Training data prepared: {training_file}'))

            file_id = fine_tuner.upload_training_file(training_file)
            self.stdout.write(self.style.SUCCESS(f'✅ Training file uploaded with ID: {file_id}'))

            # Start fine-tuning
            self.stdout.write('🚀 Starting fine-tuning job...')
            job_id = fine_tuner.create_fine_tuning_job()
            self.stdout.write(self.style.SUCCESS(f'✅ Fine-tuning job created: {job_id}'))

            # Wait for completion if requested
            if options['wait']:
                self.stdout.write('\n⏳ Waiting for fine-tuning to complete...')
                self.stdout.write('   This may take 10-30 minutes depending on data size.')
                
                final_status = self._monitor_fine_tuning(fine_tuner, job_id)
                
                if final_status.get('status') == 'succeeded':
                    model_id = final_status.get('fine_tuned_model')
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'\n🎉 Fine-tuning completed successfully!\n'
                            f'   Fine-tuned model ID: {model_id}\n'
                            f'\n📝 Next steps:'
                            f'\n   1. Update your .env file:'
                            f'\n      FALLBACK_MODEL={model_id}'
                            f'\n   2. Restart your Django server'
                            f'\n   3. Test the enhanced agent'
                        )
                    )
                else:
                    error = final_status.get('error')
                    self.stdout.write(
                        self.style.ERROR(
                            f'❌ Fine-tuning failed: {error}'
                        )
                    )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n✅ Fine-tuning job started successfully!\n'
                        f'   Job ID: {job_id}\n'
                        f'\n🔍 Monitor progress with:'
                        f'\n   python manage.py train_gpt35_fallback --data-file {options["data_file"]} --wait'
                    )
                )

        except Exception as e:
            logger.error(f"Fine-tuning error: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'❌ Error: {str(e)}')
            )
            raise 

    def _calculate_fine_tuning_cost(self, total_tokens):
        """Calculate estimated fine-tuning cost for gpt-4.1-nano"""
        # OpenAI fine-tuning costs for gpt-4.1-nano (actual pricing from user)
        cost_per_million_tokens = 0.025  # $0.025 per 1M cached input tokens for fine-tuning
        return (total_tokens / 1_000_000) * cost_per_million_tokens

    def _confirm_proceed(self, estimated_cost):
        """Ask user to confirm before proceeding with fine-tuning"""
        if estimated_cost > 5.0:  # Warn for costs over $5
            response = input(f'\n⚠️  Estimated cost is ${estimated_cost:.2f}. Proceed? (y/N): ')
            return response.lower() in ['y', 'yes']
        return True  # Auto-proceed for low costs

    def _monitor_fine_tuning(self, fine_tuner, job_id):
        """Monitor fine-tuning progress with status updates"""
        start_time = time.time()
        last_status = None
        
        while True:
            try:
                status = fine_tuner.check_fine_tuning_status(job_id)
                current_status = status.get('status')
                
                # Print status updates
                if current_status != last_status:
                    elapsed = int(time.time() - start_time)
                    self.stdout.write(
                        f'   📊 Status: {current_status} (elapsed: {elapsed}s)'
                    )
                    last_status = current_status
                
                # Check if completed
                if current_status in ['succeeded', 'failed', 'cancelled']:
                    return status
                
                # Wait before next check
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'   ⚠️  Status check failed: {e}, retrying...')
                )
                time.sleep(60)  # Wait longer on error 