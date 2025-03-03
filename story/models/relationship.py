from dataclasses import dataclass
from typing import List

@dataclass
class Relationship:
    trust: int  # -100 to 100
    interactions: List[str]
    status: str
    shared_quests: List[str] 