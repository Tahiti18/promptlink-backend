from flask import Blueprint, request, jsonify
import time
import psutil
import os
from datetime import datetime, timedelta
import random

monitoring_bp = Blueprint('monitoring', __name__)

# Simulated system metrics (in production, these would come from real monitoring)
def get_system_metrics():
    """Get real-time system metrics"""
    try:
        # Get actual system metrics where possible
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Calculate uptime (simulated for demo)
        uptime_seconds = int(time.time() % 86400)  # Reset daily for demo
        
        # Simulate some metrics based on time for demo purposes
        current_time = time.time()
        
        metrics = {
            'system_health': round(96.0 + (current_time % 8 - 4), 1),  # 92-100%
            'uptime': uptime_seconds,
            'cpu_usage': round(cpu_percent, 1),
            'memory_usage': round(memory.percent, 1),
            'disk_usage': round((disk.used / disk.total) * 100, 1),
            'active_agents': 3 + int(current_time % 3),  # 3-5 agents
            'total_combinations': 125,
            'sessions_today': 47 + int(current_time % 20),
            'total_messages': 1247 + int(current_time % 100),
            'average_response_time': round(1.2 + (current_time % 2), 2),
            'success_rate': round(98.5 + (current_time % 3 - 1.5), 1),
            'api_calls_today': 892 + int(current_time % 50),
            'errors_today': int(current_time % 5),
            'last_updated': datetime.now().isoformat()
        }
        
        return metrics
    except Exception as e:
        # Fallback metrics if system monitoring fails
        return {
            'system_health': 96.0,
            'uptime': 5439,
            'cpu_usage': 15.2,
            'memory_usage': 42.8,
            'disk_usage': 23.1,
            'active_agents': 3,
            'total_combinations': 125,
            'sessions_today': 47,
            'total_messages': 1247,
            'average_response_time': 1.2,
            'success_rate': 98.5,
            'api_calls_today': 892,
            'errors_today': 2,
            'last_updated': datetime.now().isoformat(),
            'error': str(e)
        }

@monitoring_bp.route('/monitoring/health', methods=['GET'])
def get_system_health():
    """Get overall system health status"""
    try:
        metrics = get_system_metrics()
        
        # Determine system status based on health score
        health_score = metrics['system_health']
        if health_score >= 95:
            status = 'excellent'
        elif health_score >= 90:
            status = 'good'
        elif health_score >= 80:
            status = 'fair'
        else:
            status = 'poor'
        
        health_data = {
            'status': status,
            'health_score': health_score,
            'uptime': metrics['uptime'],
            'active_agents': metrics['active_agents'],
            'total_combinations': metrics['total_combinations'],
            'last_check': metrics['last_updated'],
            'components': {
                'api_gateway': 'healthy',
                'database': 'healthy',
                'ai_models': 'healthy',
                'orchestration_engine': 'healthy'
            }
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

@monitoring_bp.route('/monitoring/metrics', methods=['GET'])
def get_metrics():
    """Get detailed system metrics"""
    try:
        metrics = get_system_metrics()
        
        return jsonify({
            'success': True,
            'metrics': metrics
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monitoring_bp.route('/monitoring/performance', methods=['GET'])
def get_performance_metrics():
    """Get performance-specific metrics"""
    try:
        metrics = get_system_metrics()
        
        performance_data = {
            'response_times': {
                'average': metrics['average_response_time'],
                'p95': round(metrics['average_response_time'] * 1.5, 2),
                'p99': round(metrics['average_response_time'] * 2.0, 2)
            },
            'throughput': {
                'requests_per_minute': round(metrics['api_calls_today'] / (metrics['uptime'] / 60), 1),
                'messages_per_hour': round(metrics['total_messages'] / (metrics['uptime'] / 3600), 1)
            },
            'reliability': {
                'success_rate': metrics['success_rate'],
                'error_rate': round(100 - metrics['success_rate'], 1),
                'uptime_percentage': round((metrics['uptime'] / 86400) * 100, 2)
            },
            'resource_usage': {
                'cpu': metrics['cpu_usage'],
                'memory': metrics['memory_usage'],
                'disk': metrics['disk_usage']
            }
        }
        
        return jsonify({
            'success': True,
            'performance': performance_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monitoring_bp.route('/monitoring/agents', methods=['GET'])
def get_agent_metrics():
    """Get agent-specific monitoring data"""
    try:
        current_time = time.time()
        
        # Simulate agent metrics
        agents_data = [
            {
                'id': 'claude',
                'name': 'Claude 3.5 Sonnet',
                'status': 'active',
                'health': round(98 + (current_time % 4 - 2), 1),
                'response_time': round(1.1 + (current_time % 1), 2),
                'requests_today': 234 + int(current_time % 30),
                'success_rate': round(99.2 + (current_time % 2 - 1), 1),
                'last_request': datetime.now().isoformat()
            },
            {
                'id': 'gpt',
                'name': 'ChatGPT 4 Turbo',
                'status': 'active',
                'health': round(95 + (current_time % 6 - 3), 1),
                'response_time': round(1.3 + (current_time % 1.5), 2),
                'requests_today': 198 + int(current_time % 25),
                'success_rate': round(98.8 + (current_time % 2 - 1), 1),
                'last_request': datetime.now().isoformat()
            },
            {
                'id': 'llama',
                'name': 'Llama 3.3',
                'status': 'active',
                'health': round(92 + (current_time % 8 - 4), 1),
                'response_time': round(1.5 + (current_time % 2), 2),
                'requests_today': 156 + int(current_time % 20),
                'success_rate': round(97.5 + (current_time % 3 - 1.5), 1),
                'last_request': datetime.now().isoformat()
            },
            {
                'id': 'mistral',
                'name': 'Mistral Large 2407',
                'status': 'active',
                'health': round(94 + (current_time % 5 - 2.5), 1),
                'response_time': round(1.4 + (current_time % 1.8), 2),
                'requests_today': 167 + int(current_time % 22),
                'success_rate': round(98.1 + (current_time % 2.5 - 1.25), 1),
                'last_request': datetime.now().isoformat()
            },
            {
                'id': 'gemini',
                'name': 'Gemini 2.0 Flash',
                'status': 'active',
                'health': round(96 + (current_time % 6 - 3), 1),
                'response_time': round(1.0 + (current_time % 1.2), 2),
                'requests_today': 189 + int(current_time % 28),
                'success_rate': round(99.0 + (current_time % 2 - 1), 1),
                'last_request': datetime.now().isoformat()
            }
        ]
        
        return jsonify({
            'success': True,
            'agents': agents_data,
            'summary': {
                'total_agents': len(agents_data),
                'active_agents': len([a for a in agents_data if a['status'] == 'active']),
                'average_health': round(sum(a['health'] for a in agents_data) / len(agents_data), 1),
                'average_response_time': round(sum(a['response_time'] for a in agents_data) / len(agents_data), 2)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monitoring_bp.route('/monitoring/alerts', methods=['GET'])
def get_alerts():
    """Get system alerts and notifications"""
    try:
        current_time = time.time()
        
        # Simulate alerts based on system state
        alerts = []
        
        metrics = get_system_metrics()
        
        # Check for potential issues
        if metrics['system_health'] < 95:
            alerts.append({
                'id': 'health_warning',
                'level': 'warning',
                'title': 'System Health Below Optimal',
                'message': f'System health is at {metrics["system_health"]}%. Consider checking system resources.',
                'timestamp': datetime.now().isoformat(),
                'resolved': False
            })
        
        if metrics['average_response_time'] > 2.0:
            alerts.append({
                'id': 'response_time_warning',
                'level': 'warning',
                'title': 'High Response Times',
                'message': f'Average response time is {metrics["average_response_time"]}s. Consider scaling resources.',
                'timestamp': datetime.now().isoformat(),
                'resolved': False
            })
        
        if metrics['errors_today'] > 5:
            alerts.append({
                'id': 'error_rate_warning',
                'level': 'error',
                'title': 'Elevated Error Rate',
                'message': f'{metrics["errors_today"]} errors detected today. Please investigate.',
                'timestamp': datetime.now().isoformat(),
                'resolved': False
            })
        
        # Add some positive alerts
        if metrics['system_health'] > 98:
            alerts.append({
                'id': 'performance_excellent',
                'level': 'info',
                'title': 'Excellent Performance',
                'message': f'System running at {metrics["system_health"]}% health. All systems optimal.',
                'timestamp': datetime.now().isoformat(),
                'resolved': True
            })
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'total_alerts': len(alerts),
            'unresolved_alerts': len([a for a in alerts if not a['resolved']])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monitoring_bp.route('/monitoring/usage', methods=['GET'])
def get_usage_stats():
    """Get usage statistics and analytics"""
    try:
        current_time = time.time()
        
        # Generate usage data for the last 7 days
        usage_data = []
        for i in range(7):
            date = datetime.now() - timedelta(days=i)
            usage_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'sessions': random.randint(30, 80),
                'messages': random.randint(800, 1500),
                'api_calls': random.randint(2000, 4000),
                'unique_users': random.randint(15, 45),
                'average_session_duration': round(random.uniform(8.5, 25.3), 1)
            })
        
        # Reverse to show oldest first
        usage_data.reverse()
        
        # Calculate totals
        total_sessions = sum(d['sessions'] for d in usage_data)
        total_messages = sum(d['messages'] for d in usage_data)
        total_api_calls = sum(d['api_calls'] for d in usage_data)
        
        usage_summary = {
            'period': '7 days',
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'total_api_calls': total_api_calls,
            'daily_average_sessions': round(total_sessions / 7, 1),
            'daily_average_messages': round(total_messages / 7, 1),
            'growth_rate': round(random.uniform(-5.2, 15.8), 1),  # Simulated growth
            'daily_data': usage_data
        }
        
        return jsonify({
            'success': True,
            'usage': usage_summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

