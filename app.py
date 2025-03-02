from flask import Flask, request, jsonify, render_template
import json
from pathlib import Path
import requests
import time

app = Flask(__name__)

HISTORY_FILE = "conversation_history.json"

def load_history():
    if Path(HISTORY_FILE).exists():
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

def generate_story_response(player_input, history):
    try:
        # Ultra-minimal prompt for maximum speed
        prompt = f"""System: You are a fantasy RPG DM. Give very short responses (10-15 words).
Player: {player_input}
Response:"""

        response = requests.post('http://localhost:11434/api/generate',
                               json={
                                   "model": "mistral",
                                   "prompt": prompt,
                                   "stream": False,
                                   "options": {
                                       "temperature": 0.5,     # Lower temperature for faster, more focused responses
                                       "top_k": 40,           # Limit token selection
                                       "top_p": 0.5,          # More focused sampling
                                       "num_predict": 20,      # Limit response length
                                       "stop": ["Player:", "Response:", "\n"],
                                       "num_ctx": 256,        # Much smaller context window
                                       "num_thread": 6,       # Increase threads
                                       "num_gpu": 1,          # Enable GPU if available
                                       "seed": 42,            # Fixed seed for faster initialization
                                       "repeat_penalty": 1.1  # Prevent repetition
                                   }
                               },
                               timeout=10)
        
        if response.status_code == 200:
            resp = response.json()['response'].strip()
            # Ensure response isn't too long
            return ' '.join(resp.split()[:15])
        else:
            print(f"Error status code: {response.status_code}")
            return "Error. Try again."
            
    except requests.exceptions.Timeout:
        print("Request timed out")
        return "Too slow. Try: 'look', 'fight', or 'run'"
    except Exception as e:
        print(f"Error: {str(e)}")
        return "Error. Try a simpler command."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/story', methods=['POST'])
def story():
    data = request.json
    player_input = data.get('input', '')
    
    # Optimize initial prompt
    if player_input.lower() == 'start game':
        return jsonify({
            'response': "You stand before a dark cave. A torch flickers nearby. What do you do?",
            'history': []
        })
    
    # Simplify player input if too long
    player_input = ' '.join(player_input.split()[:10])  # Limit to 10 words
    
    # Generate response without loading history (for speed)
    ai_response = generate_story_response(player_input, [])
    
    return jsonify({
        'response': ai_response,
        'history': []  # Don't maintain history for better performance
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001) 