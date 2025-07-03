from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
import requests
import json
from datetime import datetime

app = Flask(__name__)

# FIXED: Proper CORS configuration for Netlify
CORS(app, 
     resources={r"/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Authorization", "Accept"],
     supports_credentials=False,
     methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"])

# Additional CORS headers for preflight requests
@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization,Accept"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS,PUT,DELETE"
    response.headers["Access-Control-Max-Age"] = "86400"
    return response

# Environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://promptlink-enhanced.netlify.app')

print(f"🚀 Starting PromptLink Backend")
print(f"📡 Frontend URL: {FRONTEND_URL}")
print(f"🔑 OpenAI API Key: {'✅ Set' if OPENAI_API_KEY else '❌ Missing'}")
print(f"🔑 OpenRouter API Key: {'✅ Set' if OPENROUTER_API_KEY else '❌ Missing'}")

# Agent configurations with FIXED IDs to match frontend
AGENTS = {
    "claude3.5": {
        "id": "claude3.5",
        "name": "Claude 3.5 Sonnet",
        "model": "anthropic/claude-3.5-sonnet",
        "provider": "openrouter",
        "capabilities": ["reasoning", "analysis", "creative-writing"],
        "color": "green",
        "status": "active"
    },
    "chatgpt4": {
        "id": "chatgpt4", 
        "name": "ChatGPT 4 Turbo",
        "model": "gpt-4-turbo-preview",
        "provider": "openai",
        "capabilities": ["reasoning", "analysis", "code-generation"],
        "color": "blue",
        "status": "active"
    },
    "llama3.3": {
        "id": "llama3.3",
        "name": "Llama 3.3",
        "model": "meta-llama/llama-3.3-70b-instruct",
        "provider": "openrouter",
        "capabilities": ["reasoning", "analysis", "multilingual"],
        "color": "purple",
        "status": "active"
    },
    "mistral": {
        "id": "mistral",
        "name": "Mistral Large 2407",
        "model": "mistralai/mistral-large-2407",
        "provider": "openrouter",
        "capabilities": ["reasoning", "analysis", "code-generation"],
        "color": "orange",
        "status": "active"
    },
    "gemini": {
        "id": "gemini",
        "name": "Gemini 2.0 Flash",
        "model": "google/gemini-2.0-flash-exp",
        "provider": "openrouter",
        "capabilities": ["reasoning", "analysis", "multimodal"],
        "color": "red",
        "status": "active"
    }
}

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "service": "PromptLink Orchestration Engine",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get all available agents"""
    try:
        agents_list = []
        for agent_id, agent_config in AGENTS.items():
            agent_data = {
                **agent_config,
                "health": 95 + (hash(agent_id) % 5),  # Simulated health 95-100%
                "last_updated": datetime.now().isoformat()
            }
            agents_list.append(agent_data)
        
        return jsonify({
            "success": True,
            "total": len(agents_list),
            "active": len([a for a in agents_list if a["status"] == "active"]),
            "agents": agents_list
        })
    except Exception as e:
        print(f"❌ Error in get_agents: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

def call_openai_api(message, model="gpt-4-turbo-preview"):
    """Call OpenAI API"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": message}],
            "max_tokens": 150,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "message": result["choices"][0]["message"]["content"],
                "tokens": result["usage"]["total_tokens"]
            }
        else:
            return {
                "success": False,
                "error": f"OpenAI API error: {response.status_code} - {response.text}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"OpenAI API exception: {str(e)}"
        }

def call_openrouter_api(message, model):
    """Call OpenRouter API"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": FRONTEND_URL,
            "X-Title": "PromptLink Orchestration Engine"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": message}],
            "max_tokens": 150,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "message": result["choices"][0]["message"]["content"],
                "tokens": result["usage"]["total_tokens"]
            }
        else:
            return {
                "success": False,
                "error": f"OpenRouter API error: {response.status_code} - {response.text}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"OpenRouter API exception: {str(e)}"
        }

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    """Handle chat requests to multiple agents"""
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No JSON data provided"}), 400
        
        message = data.get('message', '').strip()
        agent_ids = data.get('agents', [])
        
        if not message:
            return jsonify({"success": False, "error": "Message is required"}), 400
        
        if not agent_ids:
            return jsonify({"success": False, "error": "At least one agent must be specified"}), 400
        
        print(f"🚀 Processing chat request:")
        print(f"📝 Message: {message}")
        print(f"🤖 Agents: {agent_ids}")
        
        responses = {}
        start_time = time.time()
        
        for agent_id in agent_ids:
            if agent_id not in AGENTS:
                responses[agent_id] = {
                    "status": "error",
                    "error": f"Unknown agent: {agent_id}",
                    "timestamp": time.time()
                }
                continue
            
            agent_config = AGENTS[agent_id]
            agent_start_time = time.time()
            
            print(f"🔄 Calling {agent_config['name']} ({agent_config['provider']})...")
            
            # Call appropriate API based on provider
            if agent_config["provider"] == "openai":
                result = call_openai_api(message, agent_config["model"])
            else:  # openrouter
                result = call_openrouter_api(message, agent_config["model"])
            
            agent_response_time = time.time() - agent_start_time
            
            if result["success"]:
                responses[agent_id] = {
                    "status": "success",
                    "response": result["message"],
                    "agent": agent_config["name"],
                    "model": agent_config["model"],
                    "timestamp": time.time(),
                    "response_time": round(agent_response_time, 2),
                    "tokens_used": result.get("tokens", 0)
                }
                print(f"✅ {agent_config['name']} responded in {agent_response_time:.2f}s")
            else:
                responses[agent_id] = {
                    "status": "error",
                    "error": result["error"],
                    "agent": agent_config["name"],
                    "timestamp": time.time(),
                    "response_time": round(agent_response_time, 2)
                }
                print(f"❌ {agent_config['name']} failed: {result['error']}")
        
        total_time = time.time() - start_time
        successful_responses = len([r for r in responses.values() if r["status"] == "success"])
        
        # FIXED: Return responses as object (not array) to match frontend expectations
        return jsonify({
            "success": True,
            "responses": responses,  # Object with agent IDs as keys
            "metadata": {
                "total_agents": len(agent_ids),
                "successful_responses": successful_responses,
                "total_time": round(total_time, 2),
                "average_response_time": round(total_time / len(agent_ids), 2) if agent_ids else 0,
                "orchestration_time": datetime.now().isoformat(),
                "session_id": f"session_{int(time.time())}"
            }
        })
        
    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "service": "PromptLink Orchestration Engine",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "agents": "/api/agents", 
            "chat": "/api/chat"
        },
        "frontend_url": FRONTEND_URL
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

