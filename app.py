from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from story_prompts import get_default_response, get_start_game_prompt, get_story_context, get_first_hint
from story_structure import StoryStructure

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret_key')
CORS(app)

# Initialize Hugging Face client
HF_TOKEN = os.environ.get('HUGGINGFACE_TOKEN')
hf_client = InferenceClient(token=HF_TOKEN) if HF_TOKEN else None

# Initialize story structure
story_structure = StoryStructure(hf_client)

@app.route('/health')
def health_check():
    return jsonify({
        "status": "ok",
        "huggingface_configured": hf_client is not None
    })

@app.route('/')
def root():
    return jsonify({
        "message": "Interactive Story API",
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

        # Update story progress based on player input
        story_structure.update_progress(player_input)
        
        # Get current story context
        context = get_story_context(
            story_structure.get_story_context(),
            player_input,
            {
                "problem": vars(story_structure.problem),
                "solution": vars(story_structure.solution)
            }
        )

        # Add philosophical guidance to the prompt
        context += "\nFocus on philosophical implications and different perspectives on truth. " \
                  "Challenge the player's assumptions while remaining engaging and thought-provoking."

        response = hf_client.text_generation(
            context,
            model="HuggingFaceH4/zephyr-7b-beta",
            max_new_tokens=200,  # Increased for more philosophical depth
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
        # Reset story state before generating new elements
        story_structure.reset_story()
        
        # Generate new story elements
        story_structure.generate_story_elements()
        
        # Get setting info for start prompt
        setting_info = {
            "location": story_structure.setting.location,
            "description": story_structure.setting.description,
            "atmosphere": story_structure.setting.atmosphere
        }
        
        # Get story structure info
        story_info = {
            "problem": vars(story_structure.problem),
            "solution": vars(story_structure.solution)
        }
        
        return jsonify({
            'response': get_start_game_prompt(setting_info, story_info),
            'story_info': {
                'setting': setting_info,
                'characters': {name: char.description for name, char in story_structure.characters.items()},
                'progress': story_structure.state.progress_percentage,
                'initial_hint': get_first_hint()
            }
        })

    # Generate response based on player input
    ai_response = generate_story_response(player_input)
    
    return jsonify({
        'response': ai_response,
        'progress': {
            'stage': story_structure.state.current_progress.value,
            'percentage': story_structure.state.progress_percentage,
            'discoveries': story_structure.state.discovered_clues,
            'actions': story_structure.state.completed_actions
        }
    })

@app.route('/api/story/debug', methods=['GET'])
def story_debug():
    """Get current story state for debugging"""
    if not app.debug:
        return jsonify({"error": "Debug endpoint only available in debug mode"}), 403
        
    return jsonify({
        'story_structure': {
            'setting': vars(story_structure.setting),
            'characters': {name: vars(char) for name, char in story_structure.characters.items()},
            'problem': vars(story_structure.problem),
            'solution': vars(story_structure.solution)
        },
        'current_state': {
            'progress': story_structure.state.current_progress.value,
            'percentage': story_structure.state.progress_percentage,
            'discoveries': story_structure.state.discovered_clues,
            'actions': story_structure.state.completed_actions
        }
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