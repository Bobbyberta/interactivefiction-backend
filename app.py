from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from story.managers.story_manager import StoryManager

# Load environment variables from .env file
load_dotenv()

# Environment configuration
IS_PRODUCTION = os.environ.get('RENDER', False)
HF_TOKEN = os.environ.get('HUGGINGFACE_TOKEN')  # Get this from Hugging Face

# Initialize Hugging Face client
hf_client = InferenceClient(token=HF_TOKEN) if HF_TOKEN else None

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret_key')
CORS(app)

# After app initialization
story_manager = StoryManager()
story_manager.set_ai_client(hf_client)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

# Define routes before any other functions
@app.route('/health')  # Note: removed methods=['GET'] to allow all methods
def health_check():
    debug_info = {
        "status": "ok",
        "environment": "production" if IS_PRODUCTION else "development",
        "huggingface_configured": hf_client is not None,
        "python_version": os.sys.version,
        "cors_origins": ["*"]
    }
    return jsonify(debug_info)

@app.route('/')
def root():
    return jsonify({
        "message": "Interactive Fiction API is running",
        "endpoints": {
            "health": "/health",
            "story": "/api/story"
        }
    })

def generate_story_response(player_input):
    try:
        print(f"\n🤖 Generating response for: {player_input}")
        
        morality_score = session.get('morality_score', 0)
        stage_change = story_manager.advance_stage(player_input, morality_score)
        
        # Get response directly from story manager
        response_text = story_manager.get_ai_response(player_input)
        
        if not response_text or not isinstance(response_text, str):
            response_text = "The story continues to unfold. You can: investigate further or seek guidance"
            
        print(f"✅ Generated response: {response_text}")
        return response_text
            
    except Exception as e:
        print(f"❌ Error generating response: {str(e)}")
        # Use a simple fallback if everything else fails
        return "The path ahead remains unclear. You can: proceed cautiously or seek another way"

def update_morality_score(player_input):
    """Update morality score based on player choices"""
    score_change = 0
    
    # Good actions
    good_keywords = ['help', 'save', 'heal', 'protect', 'share', 'friend', 'peace', 'mercy']
    # Bad actions
    bad_keywords = ['kill', 'steal', 'attack', 'lie', 'threaten', 'destroy', 'hurt']
    
    input_lower = player_input.lower()
    
    for word in good_keywords:
        if word in input_lower:
            score_change += 1
            break
            
    for word in bad_keywords:
        if word in input_lower:
            score_change -= 1
            break
    
    current_score = session.get('morality_score', 0)
    session['morality_score'] = max(min(current_score + score_change, 5), -5)  # Keep between -5 and 5
    return score_change

@app.route('/api/story', methods=['POST'])
def story():
    print("Received request:", request.json)
    data = request.json
    player_input = data.get('input', '')
    
    if player_input.lower() == 'start game':
        print("Starting new game")
        session['morality_score'] = 0
        return jsonify(story_manager.start_new_game())
    
    # Update morality score based on player's choice
    update_morality_score(player_input)
    
    player_input = ' '.join(player_input.split()[:15])
    print("Processing input:", player_input)
    
    ai_response = generate_story_response(player_input)
    print("AI response:", ai_response)
    
    return jsonify({
        'response': ai_response,
        'history': [],
        'debug_info': {  # Add debug info to response
            "world_state": story_manager.world_state.get_debug_state(),
            "current_stage": story_manager.current_stage.value,
            "stage_progress": story_manager.stage_progress,
            "resistance_count": story_manager.resistance_count
        }
    })

@app.route('/api/debug/world-state', methods=['GET'])
def get_world_state():
    if not app.debug:
        return jsonify({"error": "Debug endpoint only available in debug mode"}), 403
    
    print("\n=== WORLD STATE ===")
    print(story_manager.world_state.get_debug_state())
    print("==================\n")
    
    return jsonify({
        "world_state": story_manager.world_state.get_debug_state(),
        "current_stage": story_manager.current_stage.value,
        "stage_progress": story_manager.stage_progress,
        "resistance_count": story_manager.resistance_count
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)  # Enable debug mode 