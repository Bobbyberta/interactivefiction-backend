def get_opening_prompt() -> str:
    """Generate prompt for the opening scene"""
    return """System: You are a fantasy RPG Dungeon Master creating an opening scene for a new adventure.

Create an atmospheric opening that:
1. Sets the scene in a peaceful village
2. Introduces an inciting incident involving a mysterious message
3. Maintains a balance of mundane life and hints of adventure
4. Gives the player agency through meaningful initial choices

Format your response as:
[Time and setting description]. [Inciting incident with the mysterious message]. You can: [Read/investigate the message] or [Continue with normal routine]

Example style (but be creative and different):
"As morning mist clings to the village streets, an unexpected letter arrives bearing strange markings. You can: examine the mysterious letter or finish your morning chores"

Response:"""

def generate_story_prompt(stage, context, location_context, character_context, action_guidance) -> str:
    """Generate prompt for ongoing story"""
    return f"""System: You are a fantasy RPG Dungeon Master guiding a hero's journey.
Current stage: {stage.value}
Story tone: {context['tone']}
Focus on: {context['focus']}
Key themes: {', '.join(context['themes'])}

World Context:
{location_context}

Character Context:
{character_context}

Suggested types of actions for this stage:
{action_guidance}

IMPORTANT: Always follow this exact format:
1. Give a very brief description (5-10 words)
2. Add one key discovery that advances the current stage
3. End with "You can:" followed by EXACTLY two clear choices that progress toward the next stage

Your choices must:
- Relate directly to the current stage themes
- Move the story closer to the next stage
- Build on previous events and discoveries
- Feel natural and meaningful to the narrative
- Consider relationships with relevant characters

Example format:
"[Brief description]. [Key discovery]. You can: [choice that advances story] or [alternative meaningful choice]"
"""

def get_story_elements_prompt() -> str:
    """Generate prompt for creating consistent story elements"""
    return """System: Create a cohesive set of fantasy story elements that will be used throughout the adventure.

Generate unique elements following this structure:
- Village name: [Evocative fantasy village name]
- Village features: [3 unique features that make this village special]
- Mentor character: [Name and title of the village elder/mentor]
- Ancient threat: [The dormant danger that's awakening]
- Magical elements: [3 mystical aspects relevant to the story]
- Key locations: [3 important places and their brief descriptions]
- Prophecy: [A cryptic prediction related to the threat]
- Artifacts: [2-3 magical items that might become important]

Make all elements feel connected and consistent with each other.
Keep the tone suitable for a fantasy RPG adventure.
Ensure elements can be gradually revealed through gameplay.

Format your response as JSON:
{
    "village_name": "name",
    "village_features": ["feature1", "feature2", "feature3"],
    "mentor_name": "name",
    "mentor_title": "title",
    "ancient_threat": "description",
    "magical_elements": ["element1", "element2", "element3"],
    "key_locations": {
        "location1": "description1",
        "location2": "description2",
        "location3": "description3"
    },
    "prophecy": "prophecy text",
    "artifacts": ["artifact1", "artifact2", "artifact3"]
}

Response:""" 