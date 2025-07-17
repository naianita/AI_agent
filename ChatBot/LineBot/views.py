from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User_Info
from .agent.react_agent import ReActAgent
from .agent.model_hub import ModelHub
from .agent.tool_manager import ToolManager
import json
import logging

logger = logging.getLogger(__name__)

agent_cache = {}

def chat_interface(request):
    """Render the chat interface"""
    return render(request, 'chat.html')

def test_simple(request):
    """Simple test endpoint"""
    try:
        return JsonResponse({
            'status': 'success',
            'message': 'Simple test works!'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def test_agent(request):
    """Test agent creation"""
    try:
        model_hub = ModelHub()
        tool_manager = ToolManager()
        agent = ReActAgent(model_hub, tool_manager)
        response = agent.process_message("Hello")
        return JsonResponse({
            'status': 'success',
            'response': response
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
def chat_api(request):
    """API endpoint for chat messages"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id', 'web_user')
            message = data.get('message', '')
            
            logger.info(f"🌐 WEB INTERFACE REQUEST\nUser ID: {user_id}\nMessage: {message[:100]}{'...' if len(message) > 100 else ''}")
            
            if user_id not in agent_cache:
                logger.info(f"🚀 CREATING NEW AGENT INSTANCE for user: {user_id}")
                model_hub = ModelHub()
                tool_manager = ToolManager()
                agent_cache[user_id] = ReActAgent(model_hub, tool_manager)
            else:
                logger.info(f"♻️ REUSING EXISTING AGENT INSTANCE for user: {user_id}")
            
            agent = agent_cache[user_id]
            
            logger.info("🎯 STARTING AGENT PROCESSING...")
            response = agent.process_message(message)
            logger.info(f"✅ AGENT PROCESSING COMPLETED\nResponse length: {len(response)} characters")
            
            # Save to database - fixed to match model fields
            User_Info.objects.create(
                uid=user_id,
                name="Web User",
                mtext=message,
                response=response,
                pic_url=""
            )
            logger.info("💾 CONVERSATION SAVED TO DATABASE")
            
            return JsonResponse({
                'status': 'success',
                'response': response
            })
            
        except Exception as e:
            logger.error(f"❌ WEB API ERROR: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'response': f'Error: {str(e)}'
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def clear_memory(request):
    """Clear agent memory for testing"""
    logger.info(f"🧹 CLEARING AGENT CACHE\nCached agents: {len(agent_cache)}")
    agent_cache.clear()
    logger.info("✅ AGENT CACHE CLEARED")
    return JsonResponse({'status': 'success', 'message': 'Memory cleared'})

def get_chat_history(request):
    """Get chat history for a user"""
    try:
        user_id = request.GET.get('user_id', 'web_user')
        limit = int(request.GET.get('limit', 10))
        
        logger.info(f"📚 CHAT HISTORY REQUEST\nUser ID: {user_id}\nLimit: {limit}")
        
        messages = User_Info.objects.filter(uid=user_id).order_by('-mdt')[:limit]
        
        history = []
        for msg in reversed(messages):  # Reverse to get chronological order
            if msg.mtext:
                history.append({
                    'type': 'user',
                    'content': msg.mtext,
                    'timestamp': msg.mdt.isoformat()
                })
            if msg.response:
                history.append({
                    'type': 'assistant',
                    'content': msg.response,
                    'timestamp': msg.mdt.isoformat()
                })
        
        logger.info(f"📖 CHAT HISTORY RETRIEVED\nMessages found: {len(messages)}\nHistory items: {len(history)}")
        
        return JsonResponse({
            'status': 'success',
            'history': history
        })
        
    except Exception as e:
        logger.error(f"❌ CHAT HISTORY ERROR: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }, status=500)