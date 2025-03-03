from typing import Dict, List, Optional
from datetime import datetime
from ..models.location import Location
from ..models.event import WorldEvent
from ..models.story_elements import StoryElements

class WorldManager:
    def __init__(self):
        self.locations: Dict[str, Location] = {}
        self.events: List[WorldEvent] = []
        self.current_location: str = "village"
        
        # Initialize starting world
        self._initialize_world()
    
    def _initialize_world(self):
        """Set up initial world state"""
        self.add_location(
            "village",
            "A peaceful village nestled between ancient forests and rolling hills",
            ["forest_edge", "marketplace"],
            ["old well", "village square", "elder's house"]
        )
        
        self.add_location(
            "forest_edge",
            "The boundary where civilization meets wild nature",
            ["village", "deep_forest"],
            ["ancient stones", "worn path", "mysterious markings"]
        )
        
        self.add_location(
            "marketplace",
            "The bustling heart of village life",
            ["village", "trader_road"],
            ["merchant stalls", "town crier post", "community board"]
        )

    def add_location(self, name: str, description: str, 
                    connected_locations: List[str], notable_features: List[str]):
        """Add a new location to the world"""
        self.locations[name] = Location(
            name=name,
            description=description,
            connected_locations=connected_locations,
            notable_features=notable_features
        )

    def record_event(self, description: str, location: str, 
                    significance: str, consequences: List[str]):
        """Record a new world event"""
        event = WorldEvent(
            timestamp=datetime.now().isoformat(),
            description=description,
            location=location,
            significance=significance,
            consequences=consequences
        )
        self.events.append(event)

    def get_location_context(self, location_name: Optional[str] = None) -> str:
        """Get narrative context for a location"""
        location_name = location_name or self.current_location
        location = self.locations.get(location_name)
        
        if not location:
            return ""
        
        # Get recent events at this location
        recent_events = [
            event for event in self.events[-5:]
            if event.location == location_name
        ]
        
        context = f"""Location: {location.name}
Description: {location.description}
Notable features: {', '.join(location.notable_features)}
Connected areas: {', '.join(location.connected_locations)}
Recent events: {', '.join(event.description for event in recent_events)}"""
        
        return context

    def move_to_location(self, new_location: str) -> bool:
        """Attempt to move to a new location"""
        if new_location not in self.locations:
            return False
            
        current = self.locations.get(self.current_location)
        if not current or new_location not in current.connected_locations:
            return False
            
        self.current_location = new_location
        self.locations[new_location].discovered = True
        return True

    def get_debug_state(self) -> str:
        """Get formatted debug output of current world state"""
        return {
            "current_location": self.current_location,
            "locations": {name: vars(loc) for name, loc in self.locations.items()},
            "recent_events": [vars(event) for event in self.events[-5:]]
        }

    def initialize_world(self, story_elements: StoryElements):
        """Initialize world with generated story elements"""
        self.current_location = story_elements.village_name.lower()
        
        # Add the main village
        self.add_location(
            story_elements.village_name.lower(),
            f"A peaceful village known for {story_elements.village_features[0]}",
            [],  # Will be connected as we add other locations
            story_elements.village_features
        )
        
        # Add mentor's location
        mentor_home = f"{story_elements.mentor_name.split()[0]}'s_cottage"
        self.add_location(
            mentor_home,
            f"Home of {story_elements.mentor_name}, the {story_elements.mentor_title}",
            [story_elements.village_name.lower()],
            ["Ancient tomes", "Mystical artifacts", "Herb garden"]
        )
        
        # Add key locations from story elements
        for name, desc in story_elements.key_locations.items():
            location_id = name.lower().replace(" ", "_")
            connected_to = [story_elements.village_name.lower()]
            
            # Add some logical connections
            if "forest" in name.lower():
                connected_to.append("forest_edge")
            if "grove" in name.lower():
                connected_to.append(mentor_home)
            
            self.add_location(
                location_id,
                desc,
                connected_to,
                [f"Signs of {story_elements.magical_elements[0]}"]
            )
        
        # Update village connections after all locations are added
        village = self.locations[story_elements.village_name.lower()]
        village.connected_locations = [
            loc.name for loc in self.locations.values()
            if village.name in loc.connected_locations
        ] 