from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables from .env file
load_dotenv()

# Environment configuration
IS_PRODUCTION = os.environ.get('RENDER', False)
HF_TOKEN = os.environ.get('HUGGINGFACE_TOKEN')  # Get this from Hugging Face

# Initialize Hugging Face client
hf_client = InferenceClient(token=HF_TOKEN) if HF_TOKEN else None

app = Flask(__name__)
# Simple CORS configuration
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://bobbyberta.github.io",
            "http://localhost:8000",
            "https://bobbyberta.github.io/interactivefiction-frontend/docs"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://bobbyberta.github.io')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "message": "Interactive Fiction API is running",
        "endpoints": {
            "health": "/health",
            "story": "/api/story"
        }
    })

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    debug_info = {
        "status": "ok",
        "environment": "production" if IS_PRODUCTION else "development",
        "huggingface_configured": hf_client is not None,
        "python_version": os.sys.version,
        "cors_origins": app.config.get('CORS_ORIGINS', [])
    }
    return jsonify(debug_info)

def generate_story_response(player_input):
    try:
        print(f"🤖 Generating response for: {player_input}")
        
        # Ultra-minimal prompt for maximum speed
        prompt = f"""System: You are a fantasy RPG DM. Give very short responses (10-15 words).
Player: {player_input}
Response:"""

        response = hf_client.text_generation(
            prompt,
            model="HuggingFaceH4/zephyr-7b-beta",  # Free, good quality model
            max_new_tokens=30,
            temperature=0.7,
            stop_sequences=["Player:", "Response:", "\n"]
        )
        
        print(f"✅ Generated response: {response}")
        # Ensure response isn't too long
        return ' '.join(response.split()[:15])
            
    except Exception as e:
        print(f"❌ Error generating response: {str(e)}")
        if "rate limit" in str(e).lower():
            return "Server is busy. Please try again in a moment."
        return "Too slow. Try: 'look', 'fight', or 'run'"

@app.route('/api/story', methods=['POST'])
def story():
    print("Received request:", request.json)
    data = request.json
    player_input = data.get('input', '')
    
    # Optimize initial prompt
    if player_input.lower() == 'start game':
        print("Starting new game")
        return jsonify({
            'response': "You stand before a dark cave. A torch flickers nearby. What do you do?",
            'history': []
        })
    
    # Simplify player input if too long
    player_input = ' '.join(player_input.split()[:10])  # Limit to 10 words
    print("Processing input:", player_input)
    
    # Generate response
    ai_response = generate_story_response(player_input)
    print("AI response:", ai_response)
    
    return jsonify({
        'response': ai_response,
        'history': []
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)  # Enable debug mode 