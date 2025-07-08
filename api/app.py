from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Backend running with CORS enabled"

@app.route('/api/agents')
def get_agents():
    # Your agent logic here
    return {"agents": ["Agent1", "Agent2"]}

if __name__ == '__main__':
    app.run()
