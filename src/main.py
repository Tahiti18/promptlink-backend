import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.agents import agents_bp
from src.routes.chat import chat_bp
from src.routes.workflows import workflows_bp
from src.routes.monitoring import monitoring_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'promptlink-orchestration-engine-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS for frontend integration
CORS(app, origins=[
    'http://localhost:3000',
    'https://lucky-kheer-f8d0d3.netlify.app',
    'https://thepromptlink.com',
    os.environ.get('FRONTEND_URL', '*')
])

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(agents_bp, url_prefix='/api')
app.register_blueprint(chat_bp, url_prefix='/api')
app.register_blueprint(workflows_bp, url_prefix='/api')
app.register_blueprint(monitoring_bp, url_prefix='/api')

# Database initialization
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/health')
def health_check():
    """Health check endpoint for deployment monitoring"""
    return {
        'status': 'healthy',
        'service': 'PromptLink Orchestration Engine',
        'version': '1.0.0'
    }

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve frontend files"""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return {
                'message': 'PromptLink Orchestration Engine API',
                'version': '1.0.0',
                'endpoints': [
                    '/api/agents',
                    '/api/chat',
                    '/api/workflows',
                    '/api/monitoring',
                    '/health'
                ]
            }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
