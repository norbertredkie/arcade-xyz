"""
Map Editor Backend

Handles map creation, editing, and serialization.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid


class PropType(str, Enum):
    """Fortnite asset prop types."""
    BUILDING = "building"
    WEAPON = "weapon"
    VEHICLE = "vehicle"
    TERRAIN = "terrain"
    TRAP = "trap"
    DECORATION = "decoration"
    SPAWN_POINT = "spawn_point"
    ITEM_BOX = "item_box"


@dataclass
class Vector3:
    """3D coordinate."""
    x: float
    y: float
    z: float

    def to_dict(self) -> Dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z}


@dataclass
class Rotation:
    """Euler rotation in degrees."""
    pitch: float = 0.0
    yaw: float = 0.0
    roll: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return {"pitch": self.pitch, "yaw": self.yaw, "roll": self.roll}


@dataclass
class Prop:
    """Map prop/object."""
    id: str
    asset_id: str  # Fortnite asset ID
    name: str
    prop_type: PropType
    position: Vector3
    rotation: Rotation
    scale: Vector3 = field(default_factory=lambda: Vector3(1, 1, 1))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset_id": self.asset_id,
            "name": self.name,
            "type": self.prop_type.value,
            "position": self.position.to_dict(),
            "rotation": self.rotation.to_dict(),
            "scale": self.scale.to_dict(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Prop":
        return cls(
            id=data["id"],
            asset_id=data["asset_id"],
            name=data["name"],
            prop_type=PropType(data["type"]),
            position=Vector3(**data["position"]),
            rotation=Rotation(**data.get("rotation", {})),
            scale=Vector3(**data.get("scale", {"x": 1, "y": 1, "z": 1})),
            metadata=data.get("metadata", {}),
        )


@dataclass
class SpawnPoint:
    """Player spawn point."""
    id: str
    position: Vector3
    team: Optional[str] = None  # For team-based modes
    max_players: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "position": self.position.to_dict(),
            "team": self.team,
            "max_players": self.max_players,
        }


@dataclass
class Map:
    """Fortnite Creative map."""
    id: str
    title: str
    description: str
    creator_id: str
    props: List[Prop] = field(default_factory=list)
    spawn_points: List[SpawnPoint] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize map metadata."""
        if not self.metadata:
            self.metadata = {
                "version": "2.0.0",
                "created_at": None,
                "updated_at": None,
                "grid_size": 50,
                "bounds": {
                    "min": {"x": -10000, "y": -10000, "z": 0},
                    "max": {"x": 10000, "y": 10000, "z": 3000},
                },
            }

    def add_prop(self, prop: Prop) -> None:
        """Add prop to map."""
        self.props.append(prop)

    def remove_prop(self, prop_id: str) -> bool:
        """Remove prop from map."""
        before = len(self.props)
        self.props = [p for p in self.props if p.id != prop_id]
        return len(self.props) < before

    def add_spawn_point(self, spawn: SpawnPoint) -> None:
        """Add spawn point."""
        self.spawn_points.append(spawn)

    def get_prop(self, prop_id: str) -> Optional[Prop]:
        """Get prop by ID."""
        for prop in self.props:
            if prop.id == prop_id:
                return prop
        return None

    def update_prop(self, prop_id: str, updates: Dict[str, Any]) -> bool:
        """Update prop properties."""
        prop = self.get_prop(prop_id)
        if not prop:
            return False

        if "position" in updates:
            pos = updates["position"]
            prop.position = Vector3(**pos)
        if "rotation" in updates:
            rot = updates["rotation"]
            prop.rotation = Rotation(**rot)
        if "scale" in updates:
            scale = updates["scale"]
            prop.scale = Vector3(**scale)
        if "metadata" in updates:
            prop.metadata.update(updates["metadata"])

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Serialize map to JSON-compatible dict."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "creator_id": self.creator_id,
            "props": [p.to_dict() for p in self.props],
            "spawn_points": [s.to_dict() for s in self.spawn_points],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Map":
        """Deserialize map from JSON."""
        map_obj = cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            creator_id=data["creator_id"],
            metadata=data.get("metadata", {}),
        )

        for prop_data in data.get("props", []):
            map_obj.add_prop(Prop.from_dict(prop_data))

        for spawn_data in data.get("spawn_points", []):
            map_obj.add_spawn_point(SpawnPoint(**spawn_data))

        return map_obj


class MapBuilder:
    """Fluent API for building maps."""

    def __init__(self, title: str, description: str, creator_id: str):
        self.map = Map(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            creator_id=creator_id,
        )

    def add_prop(
        self,
        asset_id: str,
        name: str,
        prop_type: PropType,
        position: Vector3,
        rotation: Optional[Rotation] = None,
    ) -> "MapBuilder":
        """Add prop to map."""
        prop = Prop(
            id=str(uuid.uuid4()),
            asset_id=asset_id,
            name=name,
            prop_type=prop_type,
            position=position,
            rotation=rotation or Rotation(),
        )
        self.map.add_prop(prop)
        return self

    def add_spawn_point(self, position: Vector3, team: Optional[str] = None) -> "MapBuilder":
        """Add spawn point."""
        spawn = SpawnPoint(
            id=str(uuid.uuid4()),
            position=position,
            team=team,
        )
        self.map.add_spawn_point(spawn)
        return self

    def build(self) -> Map:
        """Return constructed map."""
        return self.map
