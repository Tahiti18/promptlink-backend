from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import time
import requests
import json
from datetime import datetime

# Configure Flask app to serve static files from the 'static' directory
# This assumes your index.html and other frontend assets are in a folder named 'static'
app = Flask(__name__, static_folder='static' )
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT' # You might want to change this in a real app

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
# OPENAI_API_KEY removed as it's no longer used
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
# Updated default FRONTEND_URL
FRONTEND_URL = os.getenv('FRONTEND_URL', 'web-production-2474.up.railway.app')

print(f"🚀 Starting PromptLink Backend")
print(f"📡 Frontend URL: {FRONTEND_URL}")
# OpenAI API Key print statement removed
print(f"🔑 OpenRouter API Key: {'✅ Set' if OPENROUTER_API_KEY else '❌ Missing'}")

# Agent configurations with FIXED IDs to match frontend
# Updated for DeepSeek and MinMax
AGENTS = {
    "deepseek": {
        "id": "deepseek",
        "name": "DeepSeek Coder",
        "model": "deepseek-ai/deepseek-coder",
        "provider": "openrouter",
        "capabilities": ["code-generation", "technical-analysis", "problem-solving"],
        "color": "blue",
        "status": "active"
    },
    "minmax": {
        "id": "minmax", 
        "name": "MinMax AI",
        "model": "mistralai/mixtral-8x7b-instruct", # Example model for MinMax, adjust if specific model is known
        "provider": "openrouter",
        "capabilities": ["strategic-planning", "optimization", "decision-making"],
        "color": "purple",
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

# call_openai_api function removed as it's no longer used

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
            
            # All agents now use OpenRouter
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

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    # Ensure app.static_folder is correctly set. It should be pointing to the 'static' directory.
    # If the static folder is not found, this will raise an error.
    if app.static_folder is None:
        return "Static folder not configured", 500

    # Check if the requested path is a file within the static folder
    requested_file_path = os.path.join(app.static_folder, path)
    if path != "" and os.path.exists(requested_file_path) and os.path.isfile(requested_file_path):
        return send_from_directory(app.static_folder, path)
    # If the path is empty (root URL) or the file is not found, serve index.html
    else:
        index_path = os.path.join(app.static_folder, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(app.static_folder, 'index.html')
        else:
            return "index.html not found in static folder", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
