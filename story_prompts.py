from typing import Dict

def get_default_response() -> str:
    return "The story continues... You can: look around or ask for guidance"

def get_start_game_prompt(setting: Dict, story_structure: Dict) -> str:
    """Generate dynamic opening based on the story structure"""
    return f"""Welcome to {setting['location']}, a city where reality itself is contested.

You stand at the entrance to a metropolis unlike any other. Before you, the city stretches out in distinct sectors, each controlled by different philosophical factions. In the distance, you see:

- The gleaming Truth Seeker's Archive, where absolute truth is pursued with unwavering dedication
- The organic Relativist Gardens, where multiple truths flourish side by side
- The stark Doubter's Laboratory, where reality itself is questioned
- The bustling Central Plaza, where all paths intersect

The air is thick with intellectual tension as citizens debate the nature of truth itself. Today, you must begin your journey to understand what truth means in this divided world.

You can: 
- Approach the Truth Seekers' Archive to learn about objective truth
- Visit the Relativist Gardens to explore multiple perspectives
- Head to the Doubter's Laboratory to question everything
- Observe the debates in the Central Plaza"""

def get_first_hint() -> str:
    """Get a subtle hint about the story's hidden truth"""
    return "Perhaps understanding truth requires more than choosing a single perspective..."

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
    
    return f"""You are guiding a player through a philosophical journey about the nature of truth. Stay focused on these elements:

Core Story Elements:
- Main Conflict: {main_conflict}
- Hidden Truth: {hidden_truth}
- Stakes: {stakes}

Current Story State:
- Location: {setting}
- Progress: {progress} ({story_context['progress_percentage']}% complete)
- Insights gained: {discoveries}
- Key decisions: {actions}

Story Goals Not Yet Achieved:
- Insights needed: {', '.join(d for d in needed_discoveries if d not in story_context['discovered_clues'])}
- Actions needed: {', '.join(a for a in needed_actions if a not in story_context['completed_actions'])}

Player's latest action: {player_input}

IMPORTANT GUIDELINES:
1. Each response should challenge the player's understanding of truth
2. Present multiple perspectives when appropriate
3. Encourage critical thinking and self-reflection
4. Maintain philosophical depth while remaining accessible
5. Allow player agency in forming their own conclusions

Format your response as:
[Philosophical observation or event]
You can: [Choice that explores one perspective] or [Choice that considers another view]

Response:"""

def get_character_context(character: Dict) -> str:
    """Get character-specific context for the AI"""
    return f"""Character Information:
- Name: {character['name']}
- Role: {character['role']}
- Motivation: {character['motivation']}
- Key Traits: {', '.join(character['key_traits'])}
""" 