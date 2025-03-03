from dataclasses import dataclass
from typing import List, Optional
from ..enums.character_roles import CharacterRole
from .relationship import Relationship

@dataclass
class Character:
    name: str
    role: CharacterRole
    description: str
    location: str
    knowledge: List[str]  # What they know about
    inventory: List[str]  # What they carry/own
    relationship: Relationship
    last_interaction: Optional[str] = None
    is_active: bool = True 