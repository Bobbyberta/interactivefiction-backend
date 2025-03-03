from dataclasses import dataclass
from typing import List

@dataclass
class WorldEvent:
    timestamp: str
    description: str
    location: str
    significance: str
    consequences: List[str] 