from typing import Dict

def get_default_response() -> str:
    return "The story continues... You can: look around or ask for guidance"

def get_start_game_prompt(setting: Dict, story_structure: Dict) -> str:
    """Generate dynamic opening based on the story structure"""
    main_conflict = story_structure["problem"]["main_conflict"]
    hidden_truth = story_structure["problem"]["hidden_truth"]
    first_discovery = story_structure["solution"]["required_discoveries"][0]
    
    return f"""You find yourself in {setting['location']}, {setting['description']}.
The atmosphere is {setting['atmosphere']}.
Something feels different today - {main_conflict.lower()}, though few have noticed yet.

You can: investigate the unusual atmosphere or continue with your daily routine"""

def get_first_hint() -> str:
    """Get a subtle hint about the story's hidden truth"""
    return "You sense there's more to this situation than meets the eye."

def get_story_context(story_context: Dict, player_input: str, story_structure: Dict) -> str:
    """Generate context-aware prompt for the AI"""
    progress = story_context["progress"]
    setting = story_context["setting"]
    discoveries = ", ".join(story_context["discovered_clues"]) or "none yet"
    actions = ", ".join(story_context["completed_actions"]) or "none yet"
    
    # Extract core story elements to keep AI focused
    main_conflict = story_structure["problem"]["main_conflict"]
    hidden_truth = story_structure["problem"]["hidden_truth"]
    stakes = story_structure["problem"]["stakes"]
    needed_discoveries = story_structure["solution"]["required_discoveries"]
    needed_actions = story_structure["solution"]["required_actions"]
    
    return f"""You are narrating a story with a specific plot and goals. Stay focused on the main story elements:

Core Story Elements:
- Main Conflict: {main_conflict}
- Hidden Truth: {hidden_truth}
- Stakes: {stakes}

Current Story State:
- Setting: {setting}
- Progress Stage: {progress} ({story_context['progress_percentage']}% complete)
- Discovered so far: {discoveries}
- Completed actions: {actions}

Story Goals Not Yet Achieved:
- Discoveries needed: {', '.join(d for d in needed_discoveries if d not in story_context['discovered_clues'])}
- Actions needed: {', '.join(a for a in needed_actions if a not in story_context['completed_actions'])}

Player's latest action: {player_input}

IMPORTANT GUIDELINES:
1. Every response must relate to the main conflict or hidden truth
2. Guide player toward undiscovered elements and needed actions
3. Keep all events and descriptions consistent with the core story
4. Don't introduce new conflicts or plot elements
5. Maintain focus on resolving the main story goals

Format your response as:
[Brief description that advances the main plot]
You can: [Choice that leads toward a needed discovery/action] or [Alternative choice that explores a different story goal]

Response:"""

def get_character_context(character: Dict) -> str:
    """Get character-specific context for the AI"""
    return f"""Character Information:
- Name: {character['name']}
- Role: {character['role']}
- Motivation: {character['motivation']}
- Key Traits: {', '.join(character['key_traits'])}
""" 