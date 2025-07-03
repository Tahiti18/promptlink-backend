from flask import Blueprint, request, jsonify
import time
from datetime import datetime
import json

workflows_bp = Blueprint('workflows', __name__)

# Workflow templates matching the frontend
WORKFLOW_TEMPLATES = {
    'strategic-planning': {
        'id': 'strategic-planning',
        'name': 'Strategic Planning Session',
        'description': 'Comprehensive strategic planning with multiple perspectives',
        'category': 'business',
        'estimated_time': '15-30 minutes',
        'recommended_agents': ['claude', 'gpt', 'mistral'],
        'tasks': [
            {
                'step': 1,
                'title': 'Objective Definition',
                'description': 'Define clear goals and success metrics',
                'prompt_template': 'Help me define clear, measurable objectives for: {user_input}. Focus on specific goals and success metrics.',
                'agents': ['claude', 'gpt']
            },
            {
                'step': 2,
                'title': 'Current State Analysis',
                'description': 'Current state assessment and gap identification',
                'prompt_template': 'Analyze the current state of: {user_input}. Identify key gaps and challenges that need to be addressed.',
                'agents': ['gpt', 'mistral']
            },
            {
                'step': 3,
                'title': 'Strategy Development',
                'description': 'Develop actionable implementation roadmap',
                'prompt_template': 'Based on the objectives and current state analysis, create a detailed strategic roadmap for: {user_input}.',
                'agents': ['claude', 'mistral']
            },
            {
                'step': 4,
                'title': 'Resource Planning',
                'description': 'Identify required assets and constraints',
                'prompt_template': 'Identify the resources, budget, timeline, and potential constraints for implementing: {user_input}.',
                'agents': ['gpt', 'claude']
            }
        ],
        'status': 'active',
        'usage_count': 47,
        'success_rate': 94.2
    },
    'orchestration-framework': {
        'id': 'orchestration-framework',
        'name': '5-Model Orchestration Framework',
        'description': 'Advanced multi-model coordination system',
        'category': 'ai-coordination',
        'estimated_time': '20-45 minutes',
        'recommended_agents': ['claude', 'gpt', 'llama', 'mistral', 'gemini'],
        'tasks': [
            {
                'step': 1,
                'title': 'Model Selection',
                'description': 'Choose optimal AI combination for task',
                'prompt_template': 'Analyze this task and recommend the best AI model combination: {user_input}',
                'agents': ['claude']
            },
            {
                'step': 2,
                'title': 'Role Assignment',
                'description': 'Assign specific cognitive archetypes',
                'prompt_template': 'Assign specific roles and cognitive approaches for each AI model to tackle: {user_input}',
                'agents': ['gpt', 'claude']
            },
            {
                'step': 3,
                'title': 'Collaborative Processing',
                'description': 'Enable cross-model dialogue and synthesis',
                'prompt_template': 'Work together to solve: {user_input}. Each model should contribute their unique perspective.',
                'agents': ['claude', 'gpt', 'llama', 'mistral', 'gemini']
            },
            {
                'step': 4,
                'title': 'Quality Evaluation',
                'description': 'Assess multi-model output quality',
                'prompt_template': 'Evaluate and synthesize the multi-model responses for: {user_input}. Provide a final recommendation.',
                'agents': ['claude', 'gpt']
            }
        ],
        'status': 'active',
        'usage_count': 23,
        'success_rate': 97.8
    },
    'multi-agent-debate': {
        'id': 'multi-agent-debate',
        'name': 'Multi-Agent Debate',
        'description': 'Structured debate with multiple AI perspectives',
        'category': 'analysis',
        'estimated_time': '10-25 minutes',
        'recommended_agents': ['claude', 'gpt', 'llama'],
        'tasks': [
            {
                'step': 1,
                'title': 'Position Setting',
                'description': 'Each agent takes a different stance',
                'prompt_template': 'Take a specific position on: {user_input}. Argue for your assigned perspective.',
                'agents': ['claude', 'gpt', 'llama']
            },
            {
                'step': 2,
                'title': 'Evidence Gathering',
                'description': 'Present supporting arguments',
                'prompt_template': 'Provide evidence and reasoning to support your position on: {user_input}',
                'agents': ['claude', 'gpt', 'llama']
            },
            {
                'step': 3,
                'title': 'Counter-Arguments',
                'description': 'Challenge opposing viewpoints',
                'prompt_template': 'Challenge the opposing arguments about: {user_input}. Point out weaknesses and provide rebuttals.',
                'agents': ['claude', 'gpt', 'llama']
            },
            {
                'step': 4,
                'title': 'Synthesis',
                'description': 'Find common ground and optimal solution',
                'prompt_template': 'Synthesize the debate on: {user_input}. Find common ground and propose the best solution.',
                'agents': ['claude']
            }
        ],
        'status': 'active',
        'usage_count': 31,
        'success_rate': 91.5
    }
}

@workflows_bp.route('/workflows', methods=['GET'])
def get_workflows():
    """Get all available workflow templates"""
    try:
        workflows = list(WORKFLOW_TEMPLATES.values())
        
        # Add real-time statistics
        for workflow in workflows:
            workflow['last_updated'] = datetime.now().isoformat()
            # Simulate slight usage variations
            base_usage = workflow['usage_count']
            workflow['usage_count'] = base_usage + int(time.time() % 10)
        
        return jsonify({
            'success': True,
            'workflows': workflows,
            'total': len(workflows),
            'categories': list(set(w['category'] for w in workflows))
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workflows_bp.route('/workflows/<workflow_id>', methods=['GET'])
def get_workflow(workflow_id):
    """Get specific workflow template"""
    try:
        if workflow_id not in WORKFLOW_TEMPLATES:
            return jsonify({
                'success': False,
                'error': 'Workflow not found'
            }), 404
        
        workflow = WORKFLOW_TEMPLATES[workflow_id].copy()
        workflow['last_updated'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'workflow': workflow
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workflows_bp.route('/workflows/<workflow_id>/execute', methods=['POST'])
def execute_workflow(workflow_id):
    """Execute a workflow template"""
    try:
        if workflow_id not in WORKFLOW_TEMPLATES:
            return jsonify({
                'success': False,
                'error': 'Workflow not found'
            }), 404
        
        data = request.get_json()
        user_input = data.get('input', '').strip()
        
        if not user_input:
            return jsonify({
                'success': False,
                'error': 'Input is required for workflow execution'
            }), 400
        
        workflow = WORKFLOW_TEMPLATES[workflow_id]
        
        # Create execution plan
        execution_plan = {
            'workflow_id': workflow_id,
            'workflow_name': workflow['name'],
            'user_input': user_input,
            'total_steps': len(workflow['tasks']),
            'estimated_time': workflow['estimated_time'],
            'execution_id': f"exec_{workflow_id}_{int(time.time())}",
            'status': 'ready',
            'created_at': datetime.now().isoformat(),
            'steps': []
        }
        
        # Prepare each step
        for task in workflow['tasks']:
            step = {
                'step_number': task['step'],
                'title': task['title'],
                'description': task['description'],
                'prompt': task['prompt_template'].format(user_input=user_input),
                'agents': task['agents'],
                'status': 'pending',
                'estimated_duration': '2-5 minutes'
            }
            execution_plan['steps'].append(step)
        
        return jsonify({
            'success': True,
            'execution_plan': execution_plan,
            'message': f'Workflow "{workflow["name"]}" is ready to execute with {len(workflow["tasks"])} steps'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workflows_bp.route('/workflows/executions/<execution_id>/step/<int:step_number>', methods=['POST'])
def execute_workflow_step(execution_id, step_number):
    """Execute a specific step in a workflow"""
    try:
        # This would integrate with the chat API to execute the step
        # For now, return a simulated response
        
        step_result = {
            'execution_id': execution_id,
            'step_number': step_number,
            'status': 'completed',
            'started_at': datetime.now().isoformat(),
            'completed_at': datetime.now().isoformat(),
            'duration': round(2.5 + (time.time() % 3), 1),  # Simulate 2.5-5.5 second execution
            'responses': [
                {
                    'agent': 'claude',
                    'message': f'Step {step_number} completed successfully. This is a simulated response for workflow execution.',
                    'timestamp': datetime.now().isoformat()
                }
            ],
            'next_step': step_number + 1 if step_number < 4 else None
        }
        
        return jsonify({
            'success': True,
            'step_result': step_result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workflows_bp.route('/workflows/categories', methods=['GET'])
def get_workflow_categories():
    """Get workflow categories"""
    try:
        categories = {}
        for workflow in WORKFLOW_TEMPLATES.values():
            category = workflow['category']
            if category not in categories:
                categories[category] = {
                    'name': category,
                    'workflows': [],
                    'count': 0
                }
            categories[category]['workflows'].append({
                'id': workflow['id'],
                'name': workflow['name'],
                'description': workflow['description']
            })
            categories[category]['count'] += 1
        
        return jsonify({
            'success': True,
            'categories': list(categories.values()),
            'total_categories': len(categories)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@workflows_bp.route('/workflows/stats', methods=['GET'])
def get_workflow_stats():
    """Get workflow usage statistics"""
    try:
        total_workflows = len(WORKFLOW_TEMPLATES)
        total_executions = sum(w['usage_count'] for w in WORKFLOW_TEMPLATES.values())
        avg_success_rate = sum(w['success_rate'] for w in WORKFLOW_TEMPLATES.values()) / total_workflows
        
        most_popular = max(WORKFLOW_TEMPLATES.values(), key=lambda w: w['usage_count'])
        highest_success = max(WORKFLOW_TEMPLATES.values(), key=lambda w: w['success_rate'])
        
        stats = {
            'total_workflows': total_workflows,
            'total_executions': total_executions,
            'average_success_rate': round(avg_success_rate, 1),
            'most_popular_workflow': {
                'id': most_popular['id'],
                'name': most_popular['name'],
                'usage_count': most_popular['usage_count']
            },
            'highest_success_workflow': {
                'id': highest_success['id'],
                'name': highest_success['name'],
                'success_rate': highest_success['success_rate']
            },
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

