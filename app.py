from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from story_prompts import get_default_response, get_start_game_prompt, get_story_context

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret_key')
CORS(app)

# Initialize Hugging Face client
HF_TOKEN = os.environ.get('HUGGINGFACE_TOKEN')
hf_client = InferenceClient(token=HF_TOKEN) if HF_TOKEN else None

@app.route('/health')
def health_check():
    return jsonify({
        "status": "ok",
        "huggingface_configured": hf_client is not None
    })

@app.route('/')
def root():
    return jsonify({
        "message": "AI Dungeon Master API",
        "endpoints": {
            "health": "/health",
            "story": "/api/story"
        }
    })

def generate_story_response(player_input: str) -> str:
    """Generate story response using Hugging Face"""
    try:
        if not hf_client:
            return get_default_response()

        # Get AI context from story prompts
        context = get_story_context(
            session.get('game_state', 'Starting adventure'),
            player_input
        )

        response = hf_client.text_generation(
            context,
            model="HuggingFaceH4/zephyr-7b-beta",
            max_new_tokens=150,
            temperature=0.7,
            stop_sequences=["Player:", "Response:", "\n\n"]
        )
        
        return response.strip()
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return get_default_response()

@app.route('/api/story', methods=['POST'])
def story():
    data = request.json
    player_input = data.get('input', '')

    if player_input.lower() == 'start game':
        session['game_state'] = 'beginning'
        return jsonify({
            'response': get_start_game_prompt()
        })

    # Generate response based on player input
    ai_response = generate_story_response(player_input)
    
    return jsonify({
        'response': ai_response
    })

def find_free_port(start_port: int, max_tries: int = 5) -> int:
    """Find an available port starting from start_port"""
    import socket
    for port in range(start_port, start_port + max_tries):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('0.0.0.0', port))
            sock.close()
            return port
        except OSError:
            continue
    raise OSError(f"No free ports found between {start_port} and {start_port + max_tries}")

if __name__ == '__main__':
    try:
        default_port = int(os.environ.get('PORT', 5001))
        port = find_free_port(default_port)
        print(f"Starting server on port {port}")
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        print(f"Failed to start server: {e}") 