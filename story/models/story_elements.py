from dataclasses import dataclass
from typing import List, Dict, Set

@dataclass
class StageGoal:
    description: str
    required_actions: Set[str]
    optional_actions: Set[str]
    knowledge_required: Set[str]
    completed: bool = False

@dataclass
class StageStructure:
    goals: List[StageGoal]
    theme: str
    key_events: List[str]
    locations: List[str]
    characters: List[str]

@dataclass
class StoryElements:
    village_name: str
    village_features: List[str]
    mentor_name: str
    mentor_title: str
    ancient_threat: str
    magical_elements: List[str]
    key_locations: Dict[str, str]  # name: description
    prophecy: str
    artifacts: List[str]
    stage_structure: Dict[str, StageStructure]  # Maps stage name to its structure 