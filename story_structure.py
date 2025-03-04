from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
from pprint import pprint
import json

class StoryProgress(Enum):
    INTRODUCTION = "introduction"
    RISING_ACTION = "rising_action"
    CLIMAX = "climax"
    RESOLUTION = "resolution"

@dataclass
class Character:
    name: str
    role: str  # protagonist, antagonist, supporting
    description: str
    motivation: str
    key_traits: List[str]

@dataclass
class Setting:
    location: str
    time_period: str
    description: str
    key_elements: List[str]
    atmosphere: str

@dataclass
class Problem:
    main_conflict: str
    obstacles: List[str]
    stakes: str
    hidden_truth: str  # Something the player needs to discover

@dataclass
class Solution:
    required_discoveries: List[str]  # Things player must learn
    required_actions: List[str]  # Actions player must take
    possible_outcomes: Dict[str, str]  # Different endings based on choices

@dataclass
class StoryState:
    current_progress: StoryProgress
    discovered_clues: List[str]
    completed_actions: List[str]
    relationship_scores: Dict[str, int]  # Character name: trust level
    progress_percentage: int

class StoryStructure:
    def __init__(self, hf_client):
        self.hf_client = hf_client
        self.characters: Dict[str, Character] = {}
        self.setting: Optional[Setting] = None
        self.problem: Optional[Problem] = None
        self.solution: Optional[Solution] = None
        self.state = StoryState(
            current_progress=StoryProgress.INTRODUCTION,
            discovered_clues=[],
            completed_actions=[],
            relationship_scores={},
            progress_percentage=0
        )

    def generate_story_elements(self) -> bool:
        """Generate the initial story elements"""
        try:
            prompt = """Create a story structure with the following elements in JSON format:
{
    "characters": [
        {
            "name": "character name",
            "role": "role in story",
            "description": "brief description",
            "motivation": "what drives them",
            "key_traits": ["trait1", "trait2"]
        }
    ],
    "setting": {
        "location": "where the story takes place",
        "time_period": "when it takes place",
        "description": "atmospheric description",
        "key_elements": ["important element1", "element2"],
        "atmosphere": "overall mood/feeling"
    },
    "problem": {
        "main_conflict": "central problem",
        "obstacles": ["obstacle1", "obstacle2"],
        "stakes": "what's at risk",
        "hidden_truth": "what needs to be discovered"
    },
    "solution": {
        "required_discoveries": ["discovery1", "discovery2"],
        "required_actions": ["action1", "action2"],
        "possible_outcomes": {
            "best": "description of best ending",
            "good": "description of good ending",
            "bad": "description of bad ending"
        }
    }
}

Make all elements interconnected and meaningful to the story.

Response:"""

            response = self.hf_client.text_generation(
                prompt,
                model="HuggingFaceH4/zephyr-7b-beta",
                max_new_tokens=800,
                temperature=0.7
            )

            story_data = json.loads(response.strip())

            # Create characters
            for char_data in story_data["characters"]:
                self.characters[char_data["name"]] = Character(**char_data)

            # Create setting
            self.setting = Setting(**story_data["setting"])

            # Create problem
            self.problem = Problem(**story_data["problem"])

            # Create solution
            self.solution = Solution(**story_data["solution"])

            # After successful generation, print the story structure
            print("\n=== GENERATED STORY STRUCTURE ===")
            print(f"\nSETTING: {self.setting.location}")
            print(f"Time Period: {self.setting.time_period}")
            print(f"Atmosphere: {self.setting.atmosphere}")
            
            print("\nCHARACTERS:")
            for name, char in self.characters.items():
                print(f"\n{name} ({char.role}):")
                print(f"- Description: {char.description}")
                print(f"- Motivation: {char.motivation}")
                print(f"- Traits: {', '.join(char.key_traits)}")
            
            print("\nMAIN CONFLICT:")
            print(f"Problem: {self.problem.main_conflict}")
            print(f"Stakes: {self.problem.stakes}")
            print(f"Hidden Truth: {self.problem.hidden_truth}")
            
            print("\nREQUIRED FOR SOLUTION:")
            print("Discoveries needed:")
            for disc in self.solution.required_discoveries:
                print(f"- {disc}")
            print("\nActions needed:")
            for action in self.solution.required_actions:
                print(f"- {action}")
            
            print("\n==============================\n")
            return True

        except Exception as e:
            print(f"Error generating story elements: {str(e)}")
            self._set_default_story()
            return False

    def _set_default_story(self):
        """Set default story elements if generation fails"""
        self.characters = {
            "Sarah": Character(
                name="Sarah",
                role="protagonist",
                description="A curious journalist with a keen eye for detail",
                motivation="Uncover the truth about recent mysterious events",
                key_traits=["observant", "persistent", "skeptical"]
            )
        }
        self.setting = Setting(
            location="Coastal town of Haven Bay",
            time_period="Present day",
            description="A seemingly peaceful town with dark secrets",
            key_elements=["old lighthouse", "hidden caves", "mysterious signals"],
            atmosphere="Mystery with underlying tension"
        )
        # ... add more default elements ...

    def update_progress(self, player_input: str) -> None:
        """Update story progress based on player's actions"""
        previous_progress = self.state.progress_percentage
        input_lower = player_input.lower()

        # Check for discoveries
        for discovery in self.solution.required_discoveries:
            if discovery.lower() in input_lower and discovery not in self.state.discovered_clues:
                self.state.discovered_clues.append(discovery)
                print(f"\n🔍 New Discovery: {discovery}")

        # Check for required actions
        for action in self.solution.required_actions:
            if action.lower() in input_lower and action not in self.state.completed_actions:
                self.state.completed_actions.append(action)
                print(f"\n✨ Action Completed: {action}")

        # Update progress percentage
        total_requirements = len(self.solution.required_discoveries) + len(self.solution.required_actions)
        completed = len(self.state.discovered_clues) + len(self.state.completed_actions)
        self.state.progress_percentage = int((completed / total_requirements) * 100)

        # Print progress update if changed
        if self.state.progress_percentage != previous_progress:
            print(f"\n📊 Progress Update: {self.state.progress_percentage}%")
            print(f"Stage: {self.state.current_progress.value}")
            self._print_progress_bar(self.state.progress_percentage)

        # Update story progress stage
        if self.state.progress_percentage >= 90:
            self.state.current_progress = StoryProgress.RESOLUTION
        elif self.state.progress_percentage >= 70:
            self.state.current_progress = StoryProgress.CLIMAX
        elif self.state.progress_percentage >= 30:
            self.state.current_progress = StoryProgress.RISING_ACTION

    def _print_progress_bar(self, percentage: int, width: int = 40):
        """Print a visual progress bar"""
        filled = int(width * percentage / 100)
        bar = '█' * filled + '░' * (width - filled)
        print(f"\nStory Progress: |{bar}| {percentage}%")
        print(f"Current Stage: {self.state.current_progress.value.title()}")
        
        # Show what's left to discover/do
        remaining_discoveries = [d for d in self.solution.required_discoveries 
                               if d not in self.state.discovered_clues]
        remaining_actions = [a for a in self.solution.required_actions 
                           if a not in self.state.completed_actions]
        
        if remaining_discoveries or remaining_actions:
            print("\nStill needed for story resolution:")
            if remaining_discoveries:
                print("Discoveries needed:")
                for d in remaining_discoveries:
                    print(f"- {d}")
            if remaining_actions:
                print("Actions needed:")
                for a in remaining_actions:
                    print(f"- {a}")

    def get_story_context(self) -> Dict:
        """Get current story context for AI prompt"""
        return {
            "setting": self.setting.description,
            "progress": self.state.current_progress.value,
            "discovered_clues": self.state.discovered_clues,
            "completed_actions": self.state.completed_actions,
            "progress_percentage": self.state.progress_percentage
        } 