from dataclasses import dataclass
from typing import List

@dataclass
class Location:
    name: str
    description: str
    connected_locations: List[str]
    notable_features: List[str]
    discovered: bool = False 