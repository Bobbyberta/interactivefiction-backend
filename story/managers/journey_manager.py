from typing import Dict, Optional, List, Set
from ..enums.story_stages import StoryStage
from .world_manager import WorldManager
from .character_manager import CharacterManager
from ..models.story_elements import StoryElements
from dataclasses import dataclass

@dataclass
class StageGoal:
    description: str
    required_actions: Set[str]  # Actions needed to complete this goal
    optional_actions: Set[str]  # Additional actions that contribute
    knowledge_required: Set[str]  # What the player needs to learn
    completed: bool = False

class JourneyManager:
    def __init__(self, world_manager: WorldManager, character_manager: CharacterManager):
        self.current_stage = StoryStage.ORDINARY_WORLD
        self.world_manager = world_manager
        self.character_manager = character_manager
        self.story_elements = None
        self.current_goals: List[StageGoal] = []
        self.player_knowledge: Set[str] = set()
        self.resistance_count = 0  # Keep track of player resistance
        
    @property
    def stage_progress(self) -> int:
        """Calculate progress based on completed goals"""
        if not self.current_goals:
            return 0
        completed_goals = sum(1 for goal in self.current_goals if goal.completed)
        return int((completed_goals / len(self.current_goals)) * 100)

    def initialize_journey(self, story_elements: StoryElements):
        """Initialize journey with story elements"""
        self.story_elements = story_elements
        self._set_stage_goals(self.current_stage)
        
    def _set_stage_goals(self, stage: StoryStage):
        """Set goals from story elements"""
        if not self.story_elements or not self.story_elements.stage_structure:
            return self._set_default_goals(stage)
            
        stage_structure = self.story_elements.stage_structure.get(stage.value)
        if stage_structure:
            self.current_goals = stage_structure.goals
            
            # Initialize locations for this stage
            for location in stage_structure.locations:
                if location not in self.world_manager.locations:
                    self.world_manager.add_location(location)
                    
            # Prepare characters for this stage
            for character in stage_structure.characters:
                self.character_manager.prepare_character(character)

    def advance_stage(self, player_input: str, morality_score: int) -> Optional[str]:
        """Check goal completion and advance stage if appropriate"""
        input_lower = player_input.lower()
        
        # Update player knowledge based on interactions
        self._update_knowledge(input_lower)
        
        # Check for goal-related actions
        for goal in self.current_goals:
            if any(action in input_lower for action in goal.required_actions):
                if all(knowledge in self.player_knowledge for knowledge in goal.knowledge_required):
                    goal.completed = True
            
            # Optional actions contribute to knowledge
            if any(action in input_lower for action in goal.optional_actions):
                self._add_relevant_knowledge(goal)
        
        # Check if stage should advance
        if self._should_advance_stage():
            return self._transition_stage()
            
        return None

    def _update_knowledge(self, player_input: str):
        """Update player's knowledge based on their actions"""
        if "letter" in player_input:
            self.player_knowledge.add("letter exists")
            if "read" in player_input:
                self.player_knowledge.add("dark warning")
                
        if self.story_elements:
            if "prophecy" in player_input:
                self.player_knowledge.add(self.story_elements.prophecy.lower())
            if "threat" in player_input or "danger" in player_input:
                self.player_knowledge.add(self.story_elements.ancient_threat.lower())
                
        # Add mentor-specific knowledge
        if self.story_elements and self.story_elements.mentor_name.lower() in player_input:
            self.player_knowledge.add("mentor guidance")
            if "accept" in player_input or "help" in player_input:
                self.player_knowledge.add("quest importance")

    def _should_advance_stage(self) -> bool:
        """Check if all required goals are completed"""
        return all(goal.completed for goal in self.current_goals)

    def _transition_stage(self) -> str:
        """Handle stage transition"""
        stage_transitions = {
            StoryStage.ORDINARY_WORLD: (
                StoryStage.CALL_TO_ADVENTURE,
                "The weight of destiny begins to unfold"
            ),
            StoryStage.CALL_TO_ADVENTURE: (
                StoryStage.MEETING_MENTOR,
                "The path ahead becomes clear"
            )
            # ... other transitions
        }
        
        if self.current_stage in stage_transitions:
            next_stage, transition_message = stage_transitions[self.current_stage]
            self.current_stage = next_stage
            self._set_stage_goals(next_stage)
            
            # Record the transition
            self.world_manager.record_event(
                transition_message,
                self.world_manager.current_location,
                "major",
                ["Stage transition", "Goals completed"]
            )
            
            # Check for new character introductions
            self.character_manager.check_introductions(self.current_stage)
            
            return f"Entering {self.current_stage.value}"
            
        return None

    def get_stage_context(self) -> Dict:
        """Get context from story elements"""
        if not self.story_elements or not self.story_elements.stage_structure:
            return self._get_default_context()
            
        stage_structure = self.story_elements.stage_structure.get(self.current_stage.value)
        if not stage_structure:
            return self._get_default_context()
            
        # Include progress in context
        return {
            "tone": stage_structure.theme,
            "focus": "discovery",
            "themes": [stage_structure.theme, *stage_structure.key_events],
            "suggested_actions": [
                goal.required_actions[0] for goal in self.current_goals 
                if not goal.completed and goal.required_actions
            ],
            "progress": self.stage_progress,
            "active_goals": [
                goal.description for goal in self.current_goals 
                if not goal.completed
            ]
        }

    def _get_default_context(self) -> Dict:
        """Fallback context when story elements aren't available"""
        return {
            "tone": "mysterious",
            "focus": "exploration",
            "themes": ["discovery", "adventure"],
            "suggested_actions": ["explore", "investigate", "seek guidance"],
            "progress": self.stage_progress,
            "active_goals": ["Explore your surroundings"]
        }

    def get_action_guidance(self) -> List[str]:
        """Get contextual actions for current stage"""
        context = self.get_stage_context()
        return context.get("suggested_actions", [])

    def get_stage_progress_description(self) -> str:
        """Get narrative description of current progress"""
        if self.current_stage == StoryStage.ORDINARY_WORLD:
            if self.current_goals:
                return f"Working towards: {self.current_goals[0].description}"
            else:
                return "The story is just beginning"
        elif self.current_stage == StoryStage.CALL_TO_ADVENTURE:
            if self.current_goals:
                return f"Working towards: {self.current_goals[0].description}"
            else:
                return "The story is just beginning"
        else:
            return "A turning point approaches" 