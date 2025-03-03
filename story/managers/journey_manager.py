from typing import Dict, Optional, List
from ..enums.story_stages import StoryStage
from .world_manager import WorldManager
from .character_manager import CharacterManager
from ..models.story_elements import StoryElements

class JourneyManager:
    def __init__(self, world_manager: WorldManager, character_manager: CharacterManager):
        self.current_stage = StoryStage.ORDINARY_WORLD
        self.stage_progress = 0
        self.resistance_count = 0
        self.world_manager = world_manager
        self.character_manager = character_manager
        self.story_elements = None  # Will be set during initialization
        
    def initialize_journey(self, story_elements: StoryElements):
        """Initialize journey with story elements"""
        self.story_elements = story_elements
        
    def get_stage_context(self) -> Dict:
        """Get current stage context using story elements"""
        base_context = {
            StoryStage.ORDINARY_WORLD: {
                "tone": "peaceful",
                "focus": "world building",
                "themes": ["daily life", "hidden potential", "hints of change"],
                "suggested_actions": [
                    f"explore {self.story_elements.village_name}",
                    f"visit {self.story_elements.mentor_name}",
                    "investigate strange occurrences"
                ]
            },
            StoryStage.CALL_TO_ADVENTURE: {
                "tone": "mysterious",
                "focus": "revelation",
                "themes": ["mystery", self.story_elements.ancient_threat, "call to action"],
                "suggested_actions": [
                    "seek wisdom about the prophecy",
                    "investigate magical disturbances",
                    "learn about the ancient threat"
                ]
            }
            # ... other stages ...
        }
        
        context = base_context.get(self.current_stage, base_context[StoryStage.ORDINARY_WORLD])
        
        # Add story-specific elements
        if self.story_elements:
            context["story_elements"] = {
                "threat": self.story_elements.ancient_threat,
                "magic": self.story_elements.magical_elements,
                "prophecy": self.story_elements.prophecy
            }
            
        return context

    def advance_stage(self, player_input: str, morality_score: int) -> Optional[str]:
        """Progress the story based on player choices"""
        input_lower = player_input.lower()
        
        # Track story progression triggers
        if self.current_stage == StoryStage.ORDINARY_WORLD:
            if "letter" in input_lower:
                self.stage_progress += 30
            elif "elder" in input_lower or "miriam" in input_lower or "guidance" in input_lower:
                self.stage_progress += 40
            elif "investigate" in input_lower or "explore" in input_lower:
                self.stage_progress += 20
                
        elif self.current_stage == StoryStage.CALL_TO_ADVENTURE:
            if "accept" in input_lower or "help" in input_lower:
                self.stage_progress += 40
            elif "investigate" in input_lower or "learn" in input_lower:
                self.stage_progress += 30
                
        # Check for stage transition
        if self.stage_progress >= 100:
            return self._transition_stage(player_input, morality_score)
            
        return None

    def _transition_stage(self, player_input: str, morality_score: int) -> str:
        """Handle transition between story stages"""
        stage_transitions = {
            StoryStage.ORDINARY_WORLD: StoryStage.CALL_TO_ADVENTURE,
            StoryStage.CALL_TO_ADVENTURE: StoryStage.MEETING_MENTOR,
            StoryStage.MEETING_MENTOR: StoryStage.CROSSING_THRESHOLD
        }
        
        if self.current_stage in stage_transitions:
            old_stage = self.current_stage
            self.current_stage = stage_transitions[old_stage]
            self.stage_progress = 0
            
            # Record transition event
            self.world_manager.record_event(
                f"The story moves from {old_stage.value} to {self.current_stage.value}",
                self.world_manager.current_location,
                "major",
                ["Stage transition", "New challenges ahead"]
            )
            
            # Trigger character introductions for new stage
            self.character_manager.check_introductions(self.current_stage)
            
            return f"Entering {self.current_stage.value}"
            
        return None

    def get_action_guidance(self) -> List[str]:
        """Get contextual actions for current stage"""
        context = self.get_stage_context()
        return context.get("suggested_actions", [])

    def get_stage_progress_description(self) -> str:
        """Get narrative description of current progress"""
        if self.stage_progress < 30:
            return "The story is just beginning"
        elif self.stage_progress < 60:
            return "Events are unfolding"
        elif self.stage_progress < 90:
            return "Change is imminent"
        else:
            return "A turning point approaches" 