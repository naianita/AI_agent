from django.core.management.base import BaseCommand
from LineBot.agent.react_agent import ReActAgent

class Command(BaseCommand):
    help = 'Test the ReAct agent'

    def handle(self, *args, **options):
        # Create test agent
        agent = ReActAgent("test_user")
        
        # Test queries
        test_queries = [
            "What time is it?",
            "Calculate 15 * 23",
            "Tell me about yourself",
            "What's the weather like?",
        ]
        
        for query in test_queries:
            self.stdout.write(f"\nQuery: {query}")
            response = agent.process_message(query)
            self.stdout.write(f"Response: {response}\n")