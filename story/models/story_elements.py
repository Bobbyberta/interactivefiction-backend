from dataclasses import dataclass
from typing import List, Dict

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