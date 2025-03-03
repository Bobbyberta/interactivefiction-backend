from typing import Dict, List, Optional
from dataclasses import dataclass
from ..enums.story_stages import StoryStage
from ..enums.character_roles import CharacterRole
from ..models.character import Character
from ..models.relationship import Relationship
from ..models.story_elements import StoryElements

@dataclass
class Relationship:
    trust: int  # -100 to 100
    interactions: List[str]  # History of significant interactions
    status: str  # Current state of relationship (e.g., "friendly", "hostile", "indebted")
    shared_quests: List[str]  # Quests involving this character

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
    is_active: bool = True  # Whether they're currently relevant to the story

@dataclass
class CharacterArc:
    introduction_stage: StoryStage  # When they should be introduced
    current_arc: str  # Their current story arc
    arc_progress: int  # 0-100
    development_points: List[str]  # Key character development moments

class CharacterManager:
    def __init__(self):
        self.characters: Dict[str, Character] = {}
        self.deuteragonist = None
        self.active_mentor = None
        self.supporting_characters: List[str] = []
        self.character_arcs: Dict[str, CharacterArc] = {}
        self.story_manager = None  # Will be set by StoryManager
        
    def set_story_manager(self, story_manager):
        """Set reference to story manager"""
        self.story_manager = story_manager

    def initialize_characters(self, story_elements: StoryElements):
        """Initialize characters using generated story elements"""
        # Create the mentor character
        self.add_character(
            story_elements.mentor_name,
            CharacterRole.MENTOR,
            f"{story_elements.mentor_title}, keeper of ancient knowledge",
            story_elements.village_name.lower(),
            knowledge=[
                story_elements.prophecy,
                story_elements.ancient_threat,
                *story_elements.magical_elements
            ],
            inventory=[story_elements.artifacts[0]],  # Give mentor first artifact
            current_stage=StoryStage.ORDINARY_WORLD
        )
        self.active_mentor = story_elements.mentor_name
        
        # Plan character introductions based on story elements
        self.planned_introductions = {
            StoryStage.ORDINARY_WORLD: [],  # Mentor already introduced
            StoryStage.CALL_TO_ADVENTURE: ["deuteragonist"],
            StoryStage.MEETING_MENTOR: ["supporting"],
            StoryStage.TESTS_ALLIES_ENEMIES: ["supporting", "supporting"],
            StoryStage.APPROACH_ORDEAL: ["supporting"]
        }

    def should_introduce_character(self, current_stage: StoryStage) -> Optional[str]:
        """Check if a new character should be introduced at this stage"""
        if current_stage in self.planned_introductions:
            planned_roles = self.planned_introductions[current_stage]
            if planned_roles:
                return planned_roles.pop(0)  # Get and remove the first planned role
        return None

    def add_character(self, name: str, role: CharacterRole, description: str, 
                     location: str, knowledge: List[str], inventory: List[str] = None,
                     current_stage: StoryStage = None):
        """Add a new character with role-specific handling"""
        if role == CharacterRole.SUPPORTING and len(self.supporting_characters) >= 4:
            return False
            
        relationship = Relationship(
            trust=0,
            interactions=[],
            status="neutral",
            shared_quests=[]
        )
        
        character = Character(
            name=name,
            role=role,
            description=description,
            location=location,
            knowledge=knowledge or [],
            inventory=inventory or [],
            relationship=relationship
        )
        
        # Set up character arc
        self.character_arcs[name] = CharacterArc(
            introduction_stage=current_stage,
            current_arc="introduction",
            arc_progress=0,
            development_points=[]
        )
        
        # Handle role-specific logic
        if role == CharacterRole.DEUTERAGONIST:
            self.deuteragonist = name
        elif role == CharacterRole.MENTOR:
            self.active_mentor = name
        elif role == CharacterRole.SUPPORTING:
            self.supporting_characters.append(name)
            
        self.characters[name] = character
        return True

    def advance_character_arcs(self, current_stage: StoryStage, player_input: str):
        """Progress character arcs based on story stage and interactions"""
        for name, arc in self.character_arcs.items():
            char = self.characters[name]
            
            # Check if character is mentioned in player input
            if name.lower() in player_input.lower():
                arc.arc_progress += 10
                
                # Add development point if significant progress
                if arc.arc_progress >= 100:
                    arc.development_points.append(f"Completed arc: {arc.current_arc}")
                    self._advance_character_arc(name)

    def _advance_character_arc(self, character_name: str):
        """Progress a character's arc to the next stage"""
        arc = self.character_arcs[character_name]
        char = self.characters[character_name]
        
        arc_progression = {
            "introduction": "development",
            "development": "conflict",
            "conflict": "resolution",
            "resolution": "completion"
        }
        
        if arc.current_arc in arc_progression:
            arc.current_arc = arc_progression[arc.current_arc]
            arc.arc_progress = 0

    def update_relationship(self, character_name: str, trust_change: int, 
                          interaction: str, new_status: Optional[str] = None):
        """Update relationship with a character after an interaction"""
        if character_name not in self.characters:
            return
            
        char = self.characters[character_name]
        char.relationship.trust = max(-100, min(100, char.relationship.trust + trust_change))
        char.relationship.interactions.append(interaction)
        char.last_interaction = interaction
        
        if new_status:
            char.relationship.status = new_status

    def add_shared_quest(self, character_name: str, quest: str):
        """Add a shared quest with a character"""
        if character_name in self.characters:
            self.characters[character_name].relationship.shared_quests.append(quest)

    def update_character_knowledge(self, character_name: str, new_knowledge: str):
        """Add new knowledge to a character"""
        if character_name in self.characters:
            self.characters[character_name].knowledge.append(new_knowledge)

    def get_character_context(self, character_name: str) -> str:
        """Enhanced character context including arc information"""
        if character_name not in self.characters:
            return ""
            
        char = self.characters[character_name]
        arc = self.character_arcs[character_name]
        recent_interactions = char.relationship.interactions[-3:] if char.relationship.interactions else []
        
        return f"""Character: {char.name}
Role: {char.role.value}
Description: {char.description}
Current Arc: {arc.current_arc} (Progress: {arc.arc_progress}%)
Location: {char.location}
Relationship: {char.relationship.status} (Trust: {char.relationship.trust})
Recent interactions: {', '.join(recent_interactions)}
Key knowledge: {', '.join(char.knowledge)}
Recent development: {arc.development_points[-1] if arc.development_points else 'None'}
"""

    def get_relevant_characters(self, location: str) -> List[Character]:
        """Get characters relevant to current location"""
        return [char for char in self.characters.values() 
                if char.location == location and char.is_active]

    def get_story_context(self) -> str:
        """Get relevant character context for story generation"""
        context_parts = []
        
        # Always include deuteragonist if present
        if self.deuteragonist:
            context_parts.append(f"Second Main Character: {self.get_character_context(self.deuteragonist)}")
        
        if self.active_mentor:
            context_parts.append(f"Active Mentor: {self.get_character_context(self.active_mentor)}")
        
        # Include relevant supporting characters
        if self.supporting_characters:
            supporting_context = "\nSupporting Characters:\n" + "\n".join(
                self.get_character_context(char) for char in self.supporting_characters
            )
            context_parts.append(supporting_context)
        
        return "\n".join(context_parts)

    def check_introductions(self, current_stage: StoryStage):
        """Check and handle character introductions for current stage"""
        role = self.should_introduce_character(current_stage)
        if role:
            self._prepare_character_introduction(role, current_stage)

    def _prepare_character_introduction(self, role: str, current_stage: StoryStage):
        """Create new characters using story elements"""
        if not self.story_manager or not self.story_manager.story_elements:
            return self._prepare_default_character(role, current_stage)
            
        story_elements = self.story_manager.story_elements
        
        if role == "deuteragonist":
            self.add_character(
                "Lyra",  # Could be generated
                CharacterRole.DEUTERAGONIST,
                "A traveler with knowledge of the ancient threat",
                "marketplace",
                knowledge=[
                    story_elements.ancient_threat,
                    story_elements.magical_elements[1]
                ],
                inventory=[story_elements.artifacts[1]],
                current_stage=current_stage
            )
        elif role == "mentor":
            self.add_character(
                "Elder Miriam",
                CharacterRole.MENTOR,
                "A wise village elder with knowledge of ancient prophecies",
                "village",
                ["village history", "ancient prophecies"],
                current_stage=current_stage
            )
        elif role == "supporting":
            # Add different supporting characters based on stage
            if current_stage == StoryStage.MEETING_MENTOR:
                self.add_character(
                    "Marcus",
                    CharacterRole.SUPPORTING,
                    "A skilled blacksmith with a warrior's past",
                    "village",
                    ["weaponry", "local rumors"],
                    current_stage=current_stage
                )
            # Add more supporting character introductions for other stages...

    def _prepare_default_character(self, role: str, current_stage: StoryStage):
        """Fallback character creation if story elements aren't available"""
        if role == "mentor":
            self.add_character(
                "Elder Miriam",
                CharacterRole.MENTOR,
                "A wise village elder with knowledge of ancient prophecies",
                "village",
                ["village history", "ancient prophecies"],
                current_stage=current_stage
            )
        # ... other default characters ... 

    def get_debug_state(self) -> Dict:
        """Get debug information about characters"""
        return {
            "active_characters": {
                name: {
                    "role": char.role.value,
                    "location": char.location,
                    "is_active": char.is_active,
                    "relationship": {
                        "trust": char.relationship.trust,
                        "status": char.relationship.status
                    }
                } for name, char in self.characters.items()
            },
            "deuteragonist": self.deuteragonist,
            "active_mentor": self.active_mentor,
            "supporting_characters": self.supporting_characters,
            "character_arcs": {
                name: {
                    "current_arc": arc.current_arc,
                    "progress": arc.arc_progress,
                    "developments": arc.development_points
                } for name, arc in self.character_arcs.items()
            },
            "planned_introductions": {
                stage.value: roles 
                for stage, roles in self.planned_introductions.items()
            } if hasattr(self, 'planned_introductions') else {}
        } 