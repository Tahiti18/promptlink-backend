from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import time
import requests
import json
from datetime import datetime

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
CORS(app, origins=[
    "https://promptlinkapp.netlify.app",
    "https://promptlink-experiment-1.netlify.app"
])

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', 'sk-or-v1-...')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'web-production-2474.up.railway.app')

print(f"🚀 Starting PromptLink Backend")
print(f"📡 Frontend URL: {FRONTEND_URL}")
print(f"🔑 OpenRouter API Key: {'✅ Set' if OPENROUTER_API_KEY else '❌ Missing'}")

AGENTS = {
    "deepseek": {"id": "deepseek", "name": "DeepSeek R1", "model": "deepseek/deepseek-r1",
                 "provider": "openrouter", "capabilities": ["code-generation"], "color": "blue", "status": "active", "icon": "🤖"},
    "chatgpt": {"id": "chatgpt", "name": "OpenAI GPT-4 Turbo", "model": "openai/gpt-4-turbo",
                "provider": "openrouter", "capabilities": ["conversation"], "color": "green", "status": "active", "icon": "💬"},
    "qwen": {"id": "qwen", "name": "Qwen 2.5 Coder", "model": "qwen/qwen-2.5-coder",
             "provider": "openrouter", "capabilities": ["coding"], "color": "purple", "status": "active", "icon": "🧑‍💻"},
    "llama": {"id": "llama", "name": "Meta Llama 3.3", "model": "meta-llama/llama-3-8b-instruct",
              "provider": "openrouter", "capabilities": ["text-generation"], "color": "orange", "status": "active", "icon": "🦙"},
    "mistral": {"id": "mistral", "name": "Mistral Large", "model": "mistralai/mistral-large-2407",
                "provider": "openrouter", "capabilities": ["summarization"], "color": "red", "status": "active", "icon": "💨"},
    "gpt4o": {"id": "gpt4o", "name": "GPT-4o", "model": "openai/gpt-4o",
              "provider": "openrouter", "capabilities": ["conversation"], "color": "teal", "status": "active", "icon": "💎"},
    "grok": {"id": "grok", "name": "Grok Beta", "model": "xai/grok-1.5-llama3-8b",
             "provider": "openrouter", "capabilities": ["reasoning"], "color": "brown", "status": "active", "icon": "🦾"},
    "claude": {"id": "claude", "name": "Claude Opus", "model": "anthropic/claude-3-opus",
               "provider": "openrouter", "capabilities": ["analysis"], "color": "pink", "status": "active", "icon": "🧠"},
    "gemini": {"id": "gemini", "name": "Gemini 2.0 Flash", "model": "google/gemini-1.5-flash",
               "provider": "openrouter", "capabilities": ["fast-gen"], "color": "cyan", "status": "active", "icon": "⚡"},
    "deepseekfree": {"id": "deepseekfree", "name": "DeepSeek Free", "model": "deepseek/deepseek-chat",
                     "provider": "openrouter", "capabilities": ["basic"], "color": "lightblue", "status": "active", "icon": "🔍"},
    "perplexity": {"id": "perplexity", "name": "Perplexity Pro", "model": "perplexity/perplexity-llm",
                   "provider": "openrouter", "capabilities": ["web-search"], "color": "violet", "status": "active", "icon": "🔎"}
}

def extract_message_content(agent_name, result):
    try:
        if "choices" in result and result["choices"]:
            return result["choices"][0]["message"]["content"]
        elif "output" in result:
            return result["output"]
        elif "completion" in result:
            return result["completion"]
        elif "text" in result:
            return result["text"]
        elif "answer" in result:
            return result["answer"]
        elif "result" in result:
            return result["result"]
        for key, value in result.items():
            if isinstance(value, str):
                print(f"[WARN] Fallback: using '{key}' from agent '{agent_name}'")
                return value
        for key, value in result.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, str):
                        print(f"[WARN] Fallback nested: using '{key}.{sub_key}' from agent '{agent_name}'")
                        return sub_value
        raise Exception(f"[ERROR] Unknown format from agent '{agent_name}': {result}")
    except Exception as e:
        print(f"[CRITICAL] Parsing failed for agent '{agent_name}'. Full data:\\n{result}")
        raise e

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "service": "PromptLink Orchestration Engine",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/agents', methods=['GET'])
def get_agents():
    try:
        agents_list = []
        for agent_id, agent_config in AGENTS.items():
            agent_data = {**agent_config,
                          "health": 95 + (hash(agent_id) % 5),
                          "last_updated": datetime.now().isoformat()}
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

def call_openrouter_api(message, model, agent_name):
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": f"https://{FRONTEND_URL}",
            "X-Title": "PromptLink Orchestration Engine"
        }
        if "gemini" in model:
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": message
                    }
                ]
            }
        ]
    }
else:
    data = {
        "model": model,
        "messages": [{"role": "user", "content": message}],
        "max_tokens": 2000,
        "temperature": 0.7
    }

        print(f"DEBUG MODEL USED: {model} for agent {agent_name}")

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        print(f"📡 OpenRouter response status: {response.status_code}")

        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ RAW RESPONSE from {agent_name}: {json.dumps(result, indent=2)}")
            except Exception as parse_err:
                print(f"⚠️ Failed to parse JSON from {agent_name}: {parse_err}")
                print(f"🔴 RAW BODY: {response.text}")
                raise parse_err

            message_content = extract_message_content(agent_name, result)
            return {"success": True, "message": message_content,
                    "tokens": result.get("usage", {}).get("total_tokens", 0)}
        else:
            print(f"❌ [HTTP ERROR {response.status_code}] from {agent_name}")
            print(f"🔴 RESPONSE BODY: {response.text}")
            return {"success": True, "message": f"[{agent_name} on {model} got HTTP error: {response.status_code}]", "tokens": 0}
    except Exception as e:
        print(f"❌ OpenRouter API exception: {str(e)}")
        return {"success": True, "message": f"[{agent_name} on {model} exception: {str(e)}]", "tokens": 0}

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
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
                responses[agent_id] = {"status": "error",
                                       "error": f"Unknown agent: {agent_id}",
                                       "timestamp": time.time()}
                continue
            agent_config = AGENTS[agent_id]
            agent_start_time = time.time()
            print(f"🔄 Calling {agent_config['name']} with model {agent_config['model']}...")
            result = call_openrouter_api(message, agent_config["model"], agent_config["name"])
            agent_response_time = time.time() - agent_start_time

            responses[agent_id] = {"status": "success",
                                   "response": result["message"],
                                   "agent": agent_config["name"],
                                   "model": agent_config["model"],
                                   "timestamp": time.time(),
                                   "response_time": round(agent_response_time, 2),
                                   "tokens_used": result.get("tokens", 0)}
            print(f"✅ {agent_config['name']} handled in {agent_response_time:.2f}s")

        total_time = time.time() - start_time
        return jsonify({
            "success": True,
            "responses": responses,
            "metadata": {
                "total_agents": len(agent_ids),
                "successful_responses": len(responses),
                "total_time": round(total_time, 2),
                "average_response_time": round(total_time / len(agent_ids), 2) if agent_ids else 0,
                "orchestration_time": datetime.now().isoformat(),
                "session_id": f"session_{int(time.time())}"
            }
        })
    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    if app.static_folder is None:
        return "Static folder not configured", 500
    requested_file_path = os.path.join(app.static_folder, path)
    if path != "" and os.path.exists(requested_file_path) and os.path.isfile(requested_file_path):
        return send_from_directory(app.static_folder, path)
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
