from flask import Blueprint, request, jsonify
import os
import time
from datetime import datetime

agents_bp = Blueprint('agents', __name__)

# Agent configuration matching user's existing setup
AGENT_CONFIG = {
    'claude': {
        'id': 'claude',
        'name': 'Claude 3.5 Sonnet',
        'provider': 'openrouter',
        'model': 'anthropic/claude-3.5-sonnet',
        'color': 'green',
        'capabilities': ['reasoning', 'analysis', 'creative-writing'],
        'status': 'active',
        'health': 98
    },
    'gpt': {
        'id': 'gpt',
        'name': 'ChatGPT 4 Turbo',
        'provider': 'openai',
        'model': 'gpt-4-turbo-preview',
        'color': 'blue',
        'capabilities': ['reasoning', 'analysis', 'code-generation'],
        'status': 'active',
        'health': 95
    },
    'llama': {
        'id': 'llama',
        'name': 'Llama 3.3',
        'provider': 'openrouter',
        'model': 'meta-llama/llama-3.3-70b-instruct',
        'color': 'purple',
        'capabilities': ['reasoning', 'analysis', 'multilingual'],
        'status': 'active',
        'health': 92
    },
    'mistral': {
        'id': 'mistral',
        'name': 'Mistral Large 2407',
        'provider': 'openrouter',
        'model': 'mistralai/mistral-large-2407',
        'color': 'orange',
        'capabilities': ['reasoning', 'analysis', 'code-generation'],
        'status': 'active',
        'health': 94
    },
    'gemini': {
        'id': 'gemini',
        'name': 'Gemini 2.0 Flash',
        'provider': 'openrouter',
        'model': 'google/gemini-2.0-flash-exp',
        'color': 'red',
        'capabilities': ['reasoning', 'analysis', 'multimodal'],
        'status': 'active',
        'health': 96
    }
}

@agents_bp.route('/agents', methods=['GET'])
def get_agents():
    """Get all available agents"""
    try:
        agents = list(AGENT_CONFIG.values())
        
        # Add real-time health simulation
        for agent in agents:
            # Simulate slight health variations
            base_health = agent['health']
            agent['health'] = max(85, min(100, base_health + (time.time() % 10 - 5)))
            agent['last_updated'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'agents': agents,
            'total': len(agents),
            'active': len([a for a in agents if a['status'] == 'active'])
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agents_bp.route('/agents/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    """Get specific agent details"""
    try:
        if agent_id not in AGENT_CONFIG:
            return jsonify({
                'success': False,
                'error': 'Agent not found'
            }), 404
        
        agent = AGENT_CONFIG[agent_id].copy()
        agent['last_updated'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'agent': agent
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agents_bp.route('/agents/<agent_id>/health', methods=['GET'])
def get_agent_health(agent_id):
    """Get agent health status"""
    try:
        if agent_id not in AGENT_CONFIG:
            return jsonify({
                'success': False,
                'error': 'Agent not found'
            }), 404
        
        agent = AGENT_CONFIG[agent_id]
        
        # Simulate health check
        health_data = {
            'agent_id': agent_id,
            'health': agent['health'],
            'status': agent['status'],
            'response_time': round(0.5 + (time.time() % 2), 2),  # Simulate 0.5-2.5s response time
            'last_request': datetime.now().isoformat(),
            'uptime': '99.9%',
            'requests_today': int(time.time() % 1000) + 100
        }
        
        return jsonify({
            'success': True,
            'health': health_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agents_bp.route('/agents/status', methods=['GET'])
def get_agents_status():
    """Get overall agent system status"""
    try:
        agents = list(AGENT_CONFIG.values())
        
        # Calculate system metrics
        total_agents = len(agents)
        active_agents = len([a for a in agents if a['status'] == 'active'])
        avg_health = sum(a['health'] for a in agents) / total_agents
        
        # Calculate possible combinations (5 choose 1 + 5 choose 2 + ... + 5 choose 5)
        combinations = sum(
            1 for i in range(1, total_agents + 1)
            for _ in range(2 ** i)  # Simplified combination calculation
        )
        
        status = {
            'total_agents': total_agents,
            'active_agents': active_agents,
            'average_health': round(avg_health, 1),
            'system_status': 'operational' if active_agents >= 3 else 'degraded',
            'possible_combinations': min(125, combinations),  # Cap at 125 as shown in UI
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agents_bp.route('/agents/<agent_id>/activate', methods=['POST'])
def activate_agent(agent_id):
    """Activate an agent"""
    try:
        if agent_id not in AGENT_CONFIG:
            return jsonify({
                'success': False,
                'error': 'Agent not found'
            }), 404
        
        AGENT_CONFIG[agent_id]['status'] = 'active'
        AGENT_CONFIG[agent_id]['last_updated'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'message': f'Agent {agent_id} activated',
            'agent': AGENT_CONFIG[agent_id]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@agents_bp.route('/agents/<agent_id>/deactivate', methods=['POST'])
def deactivate_agent(agent_id):
    """Deactivate an agent"""
    try:
        if agent_id not in AGENT_CONFIG:
            return jsonify({
                'success': False,
                'error': 'Agent not found'
            }), 404
        
        AGENT_CONFIG[agent_id]['status'] = 'inactive'
        AGENT_CONFIG[agent_id]['last_updated'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'message': f'Agent {agent_id} deactivated',
            'agent': AGENT_CONFIG[agent_id]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

