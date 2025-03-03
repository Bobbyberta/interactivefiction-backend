from typing import Dict, Optional, List
from ..enums.story_stages import StoryStage
from .journey_manager import JourneyManager
from .character_manager import CharacterManager
from .world_manager import WorldManager
from ..utils.story_prompts import generate_story_prompt, get_opening_prompt, get_story_elements_prompt
from random import choice
import json
from ..models.story_elements import StoryElements

class StoryManager:
    def __init__(self):
        self.world_manager = WorldManager()
        self.character_manager = CharacterManager()
        self.journey_manager = JourneyManager(self.world_manager, self.character_manager)
        self.character_manager.set_story_manager(self)
        self.last_action = ""
        self.story_beats = []  # Track key story moments
        self.player_choices = []  # Track significant choices
        self.discovered_elements = set()  # Track what player has discovered
        self.hf_client = None
        self.story_elements = None
        
    def set_ai_client(self, client):
        """Set the AI client for generating responses"""
        self.hf_client = client

    def process_response(self, response_text: str, player_input: str) -> str:
        """Guide and validate AI response based on story context"""
        try:
            self.last_action = player_input.lower()
            self.story_beats.append({"action": player_input, "stage": self.current_stage.value})
            
            # If AI response is missing or incomplete, generate new one with proper context
            if not response_text or "You can:" not in response_text:
                return self.get_ai_response(player_input)
                
            return response_text
            
        except Exception as e:
            print(f"Error in process_response: {str(e)}")
            return self._get_fallback_response()

    def get_ai_response(self, player_input: str) -> str:
        """Generate contextual story response"""
        try:
            self.last_action = player_input.lower()
            
            # Track this story beat
            story_beat = {
                "action": self.last_action,
                "stage": self.journey_manager.current_stage.value,
                "location": self.world_manager.current_location,
                "characters_present": [c.name for c in self.character_manager.get_relevant_characters(
                    self.world_manager.current_location
                )]
            }
            self.story_beats.append(story_beat)
            
            # Update discovered elements based on action
            self._update_discoveries(player_input)
            
            if not self.hf_client:
                return self._get_fallback_response()
                
            prompt = self.get_story_prompt(player_input)
            response = self.hf_client.text_generation(
                prompt,
                model="HuggingFaceH4/zephyr-7b-beta",
                max_new_tokens=150,
                temperature=0.7,
                stop_sequences=["Player:", "Response:", "\n\n"]
            )
            
            response_text = response.strip() if response else ""
            if not response_text or "You can:" not in response_text:
                return self._get_fallback_response()
                
            # Track significant choices from the response
            if "You can:" in response_text:
                choices = response_text.split("You can:")[1].strip()
                self.player_choices.append({
                    "context": response_text.split("You can:")[0].strip(),
                    "options": choices,
                    "stage": self.journey_manager.current_stage.value
                })
                
            return response_text
            
        except Exception as e:
            print(f"Error in get_ai_response: {str(e)}")
            return self._get_fallback_response()

    def _update_discoveries(self, player_input: str):
        """Track what the player has discovered"""
        input_lower = player_input.lower()
        
        # Track location discoveries
        if "explore" in input_lower or "investigate" in input_lower:
            location = self.world_manager.current_location
            self.discovered_elements.add(f"location:{location}")
            
        # Track character interactions
        for char in self.character_manager.get_relevant_characters(self.world_manager.current_location):
            if char.name.lower() in input_lower:
                self.discovered_elements.add(f"character:{char.name}")
                
        # Track key items or knowledge
        if "letter" in input_lower:
            self.discovered_elements.add("item:mysterious_letter")
        if "runes" in input_lower or "symbols" in input_lower:
            self.discovered_elements.add("knowledge:ancient_runes")

    def _get_fallback_response(self) -> str:
        """Generate a contextual fallback response"""
        try:
            stage = self.journey_manager.current_stage.value
            location = self.world_manager.current_location
            
            # Safe string checking
            if self.last_action and "letter" in self.last_action:
                return ("The mysterious letter reveals troubling news about dark forces stirring. " 
                       "Ancient warnings must not be ignored. "
                       "You can: seek Elder Miriam's counsel or investigate the forest's edge")
            
            return (f"You stand in {location}, sensing the weight of destiny. "
                    f"The {stage} phase of your journey continues. "
                    "You can: investigate your surroundings or seek guidance")
        except Exception as e:
            print(f"Error in fallback response: {str(e)}")
            # Ultimate fallback if everything else fails
            return "The path ahead remains unclear. You can: proceed cautiously or seek another way"

    def _get_stage_goal(self) -> str:
        """Get the current narrative goal based on story stage"""
        stage_goals = {
            StoryStage.ORDINARY_WORLD: "Establish the peaceful normal life and hint at coming disruption",
            StoryStage.CALL_TO_ADVENTURE: "Present a clear problem that threatens the ordinary world",
            StoryStage.MEETING_MENTOR: "Introduce wisdom and guidance while revealing the larger stakes",
            StoryStage.CROSSING_THRESHOLD: "Push the hero to make a commitment to the adventure",
            # Add goals for other stages...
        }
        return stage_goals.get(self.current_stage, "Advance the current conflict")

    def _get_narrative_focus(self) -> str:
        """Get current narrative focus based on stage and recent actions"""
        if "letter" in self.last_action and not any("letter" in beat["action"] for beat in self.story_beats[:-1]):
            return "Reveal the initial mystery and its implications"
        elif "elder" in self.last_action or "miriam" in self.last_action:
            return "Develop mentor relationship and expand story knowledge"
        elif "forest" in self.last_action:
            return "Build tension and reveal supernatural elements"
        
        # Default focus based on stage
        stage_focus = {
            StoryStage.ORDINARY_WORLD: "Show normal life while hinting at coming changes",
            StoryStage.CALL_TO_ADVENTURE: "Build urgency and present clear stakes",
            StoryStage.MEETING_MENTOR: "Share wisdom and reveal deeper truths",
            # Add focus for other stages...
        }
        return stage_focus.get(self.current_stage, "Advance the current plot thread")

    def get_story_prompt(self, player_input: str) -> str:
        """Generate dynamic story prompt based on player's journey"""
        context = self.journey_manager.get_stage_context()
        location_context = self.world_manager.get_location_context()
        character_context = self.character_manager.get_story_context()
        
        # Get recent story elements
        recent_beats = self.story_beats[-3:] if self.story_beats else []
        recent_choices = self.player_choices[-2:] if self.player_choices else []
        
        # Build narrative context
        narrative_elements = []
        for element in self.discovered_elements:
            element_type, name = element.split(":")
            if element_type == "location":
                narrative_elements.append(f"Explored {name}")
            elif element_type == "character":
                narrative_elements.append(f"Met {name}")
            elif element_type == "item":
                narrative_elements.append(f"Found {name.replace('_', ' ')}")
            elif element_type == "knowledge":
                narrative_elements.append(f"Learned about {name.replace('_', ' ')}")

        return f"""System: You are a fantasy RPG Dungeon Master creating an adaptive story.

Current stage: {self.journey_manager.current_stage.value}
Story goal: {self._get_stage_goal()}
Narrative focus: {self._get_narrative_focus()}

Player's journey so far:
- Discovered elements: {', '.join(narrative_elements)}
- Recent actions: {', '.join(beat['action'] for beat in recent_beats)}
- Previous choices: {', '.join(choice['options'] for choice in recent_choices)}

World Context:
{location_context}

Character Context:
{character_context}

Story tone: {context['tone']}
Key themes: {', '.join(context['themes'])}

IMPORTANT: Create a response that:
1. Reacts naturally to the player's action: "{player_input}"
2. Builds on their discoveries and choices
3. Advances the story while maintaining player agency
4. Offers meaningful choices that reflect current context

Format: [Vivid description of what happens]. [Key revelation or discovery]. You can: [Choice that builds on player's path] or [Alternative meaningful choice]

Response:"""

    def advance_stage(self, player_input: str, morality_score: int) -> Optional[str]:
        """Progress the story based on player input"""
        return self.journey_manager.advance_stage(player_input, morality_score)
    
    def get_debug_state(self) -> Dict:
        """Get complete debug state"""
        return {
            "world_state": self.world_manager.get_debug_state(),
            "current_stage": self.journey_manager.current_stage.value,
            "stage_progress": self.journey_manager.stage_progress,
            "resistance_count": self.journey_manager.resistance_count,
            "characters": self.character_manager.get_debug_state()
        }

    @property
    def current_stage(self):
        return self.journey_manager.current_stage

    @property
    def stage_progress(self):
        return self.journey_manager.stage_progress

    @property
    def resistance_count(self):
        return self.journey_manager.resistance_count

    @property
    def world_state(self):
        return self.world_manager 

    def generate_story_elements(self) -> StoryElements:
        """Generate consistent story elements for the game"""
        try:
            if not self.hf_client:
                return self._get_default_story_elements()

            prompt = get_story_elements_prompt()
            response = self.hf_client.text_generation(
                prompt,
                model="HuggingFaceH4/zephyr-7b-beta",
                max_new_tokens=300,
                temperature=0.7
            )

            elements = json.loads(response.strip())
            return StoryElements(**elements)
        except Exception as e:
            print(f"Error generating story elements: {str(e)}")
            return self._get_default_story_elements()

    def _get_default_story_elements(self) -> StoryElements:
        """Fallback story elements"""
        return StoryElements(
            village_name="Willowbrook",
            village_features=[
                "Ancient willow tree in the center",
                "Mysterious standing stones",
                "Bubbling healing spring"
            ],
            mentor_name="Miriam",
            mentor_title="Elder Sage",
            ancient_threat="A sealed evil in the forest depths",
            magical_elements=[
                "Nature magic",
                "Ancient runes",
                "Spirit bonds"
            ],
            key_locations={
                "Elder's Cottage": "A cozy home filled with herbs and books",
                "Sacred Grove": "Ancient trees surrounding a stone circle",
                "Whispering Falls": "A waterfall said to speak prophecies"
            },
            prophecy="When the old marks glow anew, darkness stirs in shadows true",
            artifacts=[
                "The Elder's Tome",
                "Crystal of Seeing",
                "Runestone of Sealing"
            ]
        )

    def generate_opening_scene(self) -> str:
        """Generate opening scene using story elements"""
        try:
            if not self.hf_client:
                return self._get_default_opening()

            prompt = get_opening_prompt().replace(
                "peaceful village",
                f"peaceful village of {self.story_elements.village_name}"
            )
            response = self.hf_client.text_generation(
                prompt,
                model="HuggingFaceH4/zephyr-7b-beta",
                max_new_tokens=150,
                temperature=0.8,  # Slightly higher for more variety
                stop_sequences=["Player:", "Response:", "\n\n"]
            )
            
            opening = response.strip() if response else self._get_default_opening()
            
            # Record initial story elements
            self.world_manager.record_event(
                "Story begins",
                "village",
                "major",
                ["Game start", "Peaceful beginning", "Mystery appears"]
            )
            
            return opening
            
        except Exception as e:
            print(f"Error generating opening: {str(e)}")
            return self._get_default_opening()

    def _get_default_opening(self) -> str:
        """Fallback opening if AI generation fails"""
        return ("As dawn breaks over your peaceful village, a mysterious letter arrives "
                "bearing unfamiliar markings. You can: read the letter or continue your daily routine")

    def start_new_game(self) -> Dict:
        """Initialize a new game with generated elements"""
        self.__init__()
        
        # Generate story elements first
        self.story_elements = self.generate_story_elements()
        
        # Initialize all managers with story elements
        self.world_manager.initialize_world(self.story_elements)
        self.character_manager.initialize_characters(self.story_elements)
        self.journey_manager.initialize_journey(self.story_elements)
        
        # Generate opening using story elements
        opening = self.generate_opening_scene()
        
        return {
            'response': opening,
            'history': [],
            'debug_info': self.get_debug_state()
        } 