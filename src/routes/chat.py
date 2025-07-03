from flask import Blueprint, request, jsonify
import os
import time
import requests
from datetime import datetime
import json

chat_bp = Blueprint('chat', __name__)

# API Configuration
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'
OPENAI_URL = 'https://api.openai.com/v1/chat/completions'

# Model mapping for API calls
MODEL_CONFIG = {
    'claude': {
        'api_url': OPENROUTER_URL,
        'model': 'anthropic/claude-3.5-sonnet',
        'api_key': OPENROUTER_API_KEY,
        'headers': {
            'Authorization': f'Bearer {OPENROUTER_API_KEY}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://thepromptlink.com',
            'X-Title': 'PromptLink Enhanced'
        }
    },
    'gpt': {
        'api_url': OPENAI_URL,
        'model': 'gpt-4-turbo-preview',
        'api_key': OPENAI_API_KEY,
        'headers': {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
    },
    'llama': {
        'api_url': OPENROUTER_URL,
        'model': 'meta-llama/llama-3.3-70b-instruct',
        'api_key': OPENROUTER_API_KEY,
        'headers': {
            'Authorization': f'Bearer {OPENROUTER_API_KEY}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://thepromptlink.com',
            'X-Title': 'PromptLink Enhanced'
        }
    },
    'mistral': {
        'api_url': OPENROUTER_URL,
        'model': 'mistralai/mistral-large-2407',
        'api_key': OPENROUTER_API_KEY,
        'headers': {
            'Authorization': f'Bearer {OPENROUTER_API_KEY}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://thepromptlink.com',
            'X-Title': 'PromptLink Enhanced'
        }
    },
    'gemini': {
        'api_url': OPENROUTER_URL,
        'model': 'google/gemini-2.0-flash-exp',
        'api_key': OPENROUTER_API_KEY,
        'headers': {
            'Authorization': f'Bearer {OPENROUTER_API_KEY}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://thepromptlink.com',
            'X-Title': 'PromptLink Enhanced'
        }
    }
}

def call_ai_model(agent_id, message, mode='free'):
    """Call AI model API"""
    if agent_id not in MODEL_CONFIG:
        raise ValueError(f"Unknown agent: {agent_id}")
    
    config = MODEL_CONFIG[agent_id]
    
    # Check if API key is available
    if not config['api_key']:
        # Return demo response if no API key
        return {
            'agent': agent_id,
            'message': f"Demo response from {agent_id}: I received your message '{message}'. In production, this would be a real AI response using your existing API keys.",
            'timestamp': datetime.now().isoformat(),
            'demo_mode': True
        }
    
    # Prepare system prompt based on mode
    system_prompts = {
        'debate': f"You are participating in a structured debate. Take a clear position and provide well-reasoned arguments.",
        'brainstorm': f"You are in a creative brainstorming session. Generate innovative ideas and build upon concepts.",
        'plan': f"You are helping create a strategic plan. Focus on actionable steps and practical implementation.",
        'free': f"You are an AI assistant ready to help with any task. Respond naturally and helpfully."
    }
    
    system_prompt = system_prompts.get(mode, system_prompts['free'])
    
    # Prepare API request
    payload = {
        'model': config['model'],
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': message}
        ],
        'max_tokens': 1000,
        'temperature': 0.7
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            config['api_url'],
            headers=config['headers'],
            json=payload,
            timeout=30
        )
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            ai_message = data['choices'][0]['message']['content']
            
            return {
                'agent': agent_id,
                'message': ai_message,
                'timestamp': datetime.now().isoformat(),
                'response_time': round(response_time, 2),
                'tokens_used': data.get('usage', {}).get('total_tokens', 0),
                'demo_mode': False
            }
        else:
            # Fallback to demo response on API error
            return {
                'agent': agent_id,
                'message': f"API Error - Demo response from {agent_id}: I received your message '{message}'. Please check your API configuration.",
                'timestamp': datetime.now().isoformat(),
                'error': f"API returned status {response.status_code}",
                'demo_mode': True
            }
            
    except Exception as e:
        # Fallback to demo response on any error
        return {
            'agent': agent_id,
            'message': f"Connection Error - Demo response from {agent_id}: I received your message '{message}'. Please check your network connection and API keys.",
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'demo_mode': True
        }

@chat_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests with AI orchestration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        message = data.get('message', '').strip()
        agents = data.get('agents', ['claude'])  # Default to Claude
        mode = data.get('mode', 'free')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        if not agents:
            agents = ['claude']  # Default agent
        
        # Ensure agents is a list
        if isinstance(agents, str):
            agents = [agents]
        
        # Validate agents
        valid_agents = [agent for agent in agents if agent in MODEL_CONFIG]
        if not valid_agents:
            return jsonify({
                'success': False,
                'error': 'No valid agents specified'
            }), 400
        
        # Call AI models
        responses = []
        total_tokens = 0
        total_response_time = 0
        
        for agent_id in valid_agents:
            try:
                response = call_ai_model(agent_id, message, mode)
                responses.append(response)
                total_tokens += response.get('tokens_used', 0)
                total_response_time += response.get('response_time', 0)
            except Exception as e:
                # Add error response for failed agent
                responses.append({
                    'agent': agent_id,
                    'message': f"Error: Could not get response from {agent_id}. {str(e)}",
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e),
                    'demo_mode': True
                })
        
        # Calculate orchestration metadata
        metadata = {
            'total_agents': len(valid_agents),
            'successful_responses': len([r for r in responses if not r.get('error')]),
            'total_tokens': total_tokens,
            'average_response_time': round(total_response_time / len(responses), 2) if responses else 0,
            'mode': mode,
            'orchestration_time': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'responses': responses,
            'metadata': metadata,
            'session_id': f"session_{int(time.time())}"
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/chat/single', methods=['POST'])
def chat_single():
    """Handle single agent chat (backward compatibility)"""
    try:
        data = request.get_json()
        
        message = data.get('message', '').strip()
        agent = data.get('agent', 'claude')
        mode = data.get('mode', 'free')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Call single AI model
        response = call_ai_model(agent, message, mode)
        
        return jsonify({
            'success': True,
            'response': response,
            'session_id': f"session_{int(time.time())}"
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@chat_bp.route('/chat/models', methods=['GET'])
def get_available_models():
    """Get list of available AI models"""
    try:
        models = []
        for agent_id, config in MODEL_CONFIG.items():
            models.append({
                'id': agent_id,
                'name': config['model'],
                'provider': 'openrouter' if 'openrouter' in config['api_url'] else 'openai',
                'available': bool(config['api_key']),
                'demo_mode': not bool(config['api_key'])
            })
        
        return jsonify({
            'success': True,
            'models': models,
            'total': len(models),
            'available': len([m for m in models if m['available']])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

