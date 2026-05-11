"""
Map Optimization & Validation Engine

Validates maps against Fortnite Creative specs and provides optimization suggestions.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    """Issue severity level."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Single validation issue."""
    severity: Severity
    code: str
    message: str
    suggestion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity.value,
            "code": self.code,
            "message": self.message,
            "suggestion": self.suggestion,
        }


class FortniteSpecs:
    """Fortnite Creative mode technical specifications."""

    # Performance limits
    MAX_POLY_COUNT = 500_000
    MAX_MEMORY_MB = 256
    MAX_PROPS = 10_000
    MAX_SPAWN_POINTS = 100
    MAX_TEXTURE_RESOLUTION = 4096

    # Gameplay balance
    MIN_SPAWN_POINTS = 2
    MIN_WEAPON_SPAWNS = 1
    MAX_WEAPONS_PER_AREA = 5
    WEAPON_MINIMUM_DISTANCE = 100  # Unreal units

    # World bounds
    WORLD_MIN_X = -10000
    WORLD_MAX_X = 10000
    WORLD_MIN_Y = -10000
    WORLD_MAX_Y = 10000
    WORLD_MIN_Z = 0
    WORLD_MAX_Z = 3000


class MapValidator:
    """Validates map against Fortnite Creative specs."""

    def __init__(self):
        self.issues: List[ValidationIssue] = []

    def validate(self, map_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run all validation checks."""
        self.issues = []

        # Structural checks
        self._validate_metadata(map_data)
        self._validate_bounds(map_data)
        self._validate_props(map_data)
        self._validate_spawn_points(map_data)
        self._validate_gameplay_balance(map_data)

        return self.get_report()

    def _validate_metadata(self, map_data: Dict[str, Any]) -> None:
        """Validate map metadata."""
        required_fields = ["title", "description", "creator_id"]
        for field in required_fields:
            if field not in map_data:
                self.issues.append(
                    ValidationIssue(
                        Severity.ERROR,
                        "MISSING_FIELD",
                        f"Missing required field: {field}",
                    )
                )

        if len(map_data.get("title", "")) < 3:
            self.issues.append(
                ValidationIssue(
                    Severity.ERROR,
                    "TITLE_TOO_SHORT",
                    "Map title must be at least 3 characters",
                )
            )

    def _validate_bounds(self, map_data: Dict[str, Any]) -> None:
        """Validate world bounds."""
        props = map_data.get("props", [])
        out_of_bounds = 0

        for prop in props:
            pos = prop.get("position", {})
            x, y, z = pos.get("x", 0), pos.get("y", 0), pos.get("z", 0)

            if not (
                FortniteSpecs.WORLD_MIN_X <= x <= FortniteSpecs.WORLD_MAX_X
                and FortniteSpecs.WORLD_MIN_Y <= y <= FortniteSpecs.WORLD_MAX_Y
                and FortniteSpecs.WORLD_MIN_Z <= z <= FortniteSpecs.WORLD_MAX_Z
            ):
                out_of_bounds += 1

        if out_of_bounds > 0:
            self.issues.append(
                ValidationIssue(
                    Severity.ERROR,
                    "OUT_OF_BOUNDS",
                    f"{out_of_bounds} props are outside world bounds",
                    suggestion="Move props within bounds or adjust world size",
                )
            )

    def _validate_props(self, map_data: Dict[str, Any]) -> None:
        """Validate prop count and performance."""
        props = map_data.get("props", [])
        prop_count = len(props)

        # Prop count limit
        if prop_count > FortniteSpecs.MAX_PROPS:
            self.issues.append(
                ValidationIssue(
                    Severity.ERROR,
                    "TOO_MANY_PROPS",
                    f"{prop_count} props exceeds limit of {FortniteSpecs.MAX_PROPS}",
                    suggestion=f"Remove {prop_count - FortniteSpecs.MAX_PROPS} props",
                )
            )

        # Estimate poly count (rough)
        estimated_polys = prop_count * 500  # Avg 500 polys per prop
        if estimated_polys > FortniteSpecs.MAX_POLY_COUNT:
            self.issues.append(
                ValidationIssue(
                    Severity.WARNING,
                    "HIGH_POLY_COUNT",
                    f"Estimated {estimated_polys} polys may exceed {FortniteSpecs.MAX_POLY_COUNT} limit",
                    suggestion="Remove or simplify props, especially decoration",
                )
            )

    def _validate_spawn_points(self, map_data: Dict[str, Any]) -> None:
        """Validate spawn point coverage."""
        spawns = map_data.get("spawn_points", [])
        spawn_count = len(spawns)

        if spawn_count < FortniteSpecs.MIN_SPAWN_POINTS:
            self.issues.append(
                ValidationIssue(
                    Severity.ERROR,
                    "INSUFFICIENT_SPAWNS",
                    f"Only {spawn_count} spawn points; minimum is {FortniteSpecs.MIN_SPAWN_POINTS}",
                    suggestion="Add more spawn points for team/deathmatch modes",
                )
            )

        if spawn_count > FortniteSpecs.MAX_SPAWN_POINTS:
            self.issues.append(
                ValidationIssue(
                    Severity.WARNING,
                    "TOO_MANY_SPAWNS",
                    f"{spawn_count} spawn points may overcrowd the map",
                    suggestion="Consider removing redundant spawn points",
                )
            )

    def _validate_gameplay_balance(self, map_data: Dict[str, Any]) -> None:
        """Validate weapon placement and balance."""
        props = map_data.get("props", [])
        weapons = [p for p in props if p.get("type") == "weapon"]
        weapon_count = len(weapons)

        if weapon_count < FortniteSpecs.MIN_WEAPON_SPAWNS:
            self.issues.append(
                ValidationIssue(
                    Severity.ERROR,
                    "NO_WEAPONS",
                    f"Map has no weapon spawns; minimum is {FortniteSpecs.MIN_WEAPON_SPAWNS}",
                    suggestion="Add weapon spawns to combat areas",
                )
            )

        # Check weapon spacing
        for i, weapon1 in enumerate(weapons):
            pos1 = weapon1.get("position", {})
            nearby = 0
            for weapon2 in weapons[i + 1:]:
                pos2 = weapon2.get("position", {})
                dx = pos1.get("x", 0) - pos2.get("x", 0)
                dy = pos1.get("y", 0) - pos2.get("y", 0)
                distance = (dx**2 + dy**2) ** 0.5

                if distance < FortniteSpecs.WEAPON_MINIMUM_DISTANCE:
                    nearby += 1

            if nearby > FortniteSpecs.MAX_WEAPONS_PER_AREA:
                self.issues.append(
                    ValidationIssue(
                        Severity.WARNING,
                        "WEAPON_CLUSTERING",
                        f"Too many weapons clustered near {pos1}",
                        suggestion="Spread weapons across the map for better balance",
                    )
                )

    def get_report(self) -> Dict[str, Any]:
        """Get validation report."""
        errors = [i for i in self.issues if i.severity == Severity.ERROR]
        warnings = [i for i in self.issues if i.severity == Severity.WARNING]

        return {
            "valid": len(errors) == 0,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "issues": [issue.to_dict() for issue in self.issues],
        }
