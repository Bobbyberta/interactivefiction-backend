def get_default_response() -> str:
    return "The path ahead remains unclear. You can: proceed cautiously or seek another way"

def get_start_game_prompt() -> str:
    return """You find yourself in a peaceful village as dawn breaks. A mysterious letter arrives bearing unfamiliar markings.
You can: read the letter or continue your daily routine"""

def get_story_context(game_state: str, player_input: str) -> str:
    return f"""You are a fantasy RPG Dungeon Master creating an engaging interactive story. 

Key guidelines:
- Keep responses concise but vivid
- Maintain consistent story elements
- Offer meaningful choices that affect the story
- React naturally to player decisions
- Include elements of mystery and adventure

Current game state: {game_state}
Player action: {player_input}

Format your response as:
[Brief, vivid description of what happens]
You can: [Meaningful choice 1] or [Meaningful choice 2]

Note: Each choice should:
- Be clear and actionable
- Lead to different story paths
- Feel consequential to the story

Response:""" 