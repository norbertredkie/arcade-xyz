"""
Map optimization engine - AI-powered suggestions for map improvements
"""

import json
import logging
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OptimizationSuggestion:
    """A single optimization suggestion."""

    suggestion_id: str
    issue_type: str  # "weapon_balance", "spawn_spacing", "healing_placement", etc.
    description: str  # What's wrong
    suggestion: str  # What to do
    cost_credits: int  # Cost to implement
    impact: str  # "balance", "playability", "spacing", "flow"
    priority: str  # "critical", "high", "medium", "low"


class MapOptimizer:
    """Analyze maps and generate optimization suggestions."""

    def __init__(self, validator):
        """Initialize with map validator."""
        self.validator = validator

    def analyze_and_suggest(
        self, map_data: Dict[str, Any]
    ) -> Tuple[List[OptimizationSuggestion], Dict[str, Any]]:
        """
        Analyze a map and generate optimization suggestions.
        
        Returns: (suggestions, analysis_results)
        """
        # First, run validator
        analysis = self.validator.validate(map_data)

        suggestions = []

        # Analyze each issue and create suggestion
        for issue in analysis.get("issues", []):
            issue_type = issue.get("type")
            message = issue.get("message", "")

            suggestion = self._create_suggestion(issue_type, message, map_data)
            if suggestion:
                suggestions.append(suggestion)

        # Also do proactive suggestions (things not in validation)
        proactive = self._generate_proactive_suggestions(map_data, analysis)
        suggestions.extend(proactive)

        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        suggestions.sort(
            key=lambda x: priority_order.get(x.priority, 99)
        )

        logger.info(
            f"🔍 Generated {len(suggestions)} suggestions for map: {map_data.get('title')}"
        )
        return suggestions, analysis

    def _create_suggestion(
        self, issue_type: str, message: str, map_data: Dict[str, Any]
    ) -> OptimizationSuggestion:
        """Create a suggestion from a validation issue."""
        import uuid

        # Map issue type to suggestion template
        templates = {
            "weapon_balance": {
                "description": "Weapon distribution is unbalanced across the map",
                "suggestion": "Rebalance weapon placement to match team spawns",
                "cost": 5,
                "impact": "balance",
                "priority": "high",
            },
            "spawn_spacing": {
                "description": "Team spawn points are too close together",
                "suggestion": "Spread team spawns further apart to prevent collision",
                "cost": 3,
                "impact": "playability",
                "priority": "high",
            },
            "healing_placement": {
                "description": "Healing items are not strategically placed",
                "suggestion": "Add healing near high-combat zones and side routes",
                "cost": 2,
                "impact": "balance",
                "priority": "medium",
            },
            "prop_coverage": {
                "description": "Insufficient cover or prop placement",
                "suggestion": "Add more cover/props for tactical gameplay",
                "cost": 2,
                "impact": "playability",
                "priority": "medium",
            },
            "map_flow": {
                "description": "Map flow is poor - limited rotation options",
                "suggestion": "Add additional routes/connections between areas",
                "cost": 3,
                "impact": "flow",
                "priority": "medium",
            },
            "out_of_bounds": {
                "description": "Some props are outside map boundaries",
                "suggestion": "Move out-of-bounds props back within boundaries",
                "cost": 2,
                "impact": "playability",
                "priority": "critical",
            },
        }

        template = templates.get(issue_type)
        if not template:
            # Generic suggestion for unknown issue
            template = {
                "description": message,
                "suggestion": f"Review and fix: {message}",
                "cost": 3,
                "impact": "general",
                "priority": "low",
            }

        return OptimizationSuggestion(
            suggestion_id=str(uuid.uuid4()),
            issue_type=issue_type,
            description=template["description"],
            suggestion=template["suggestion"],
            cost_credits=template["cost"],
            impact=template["impact"],
            priority=template["priority"],
        )

    def _generate_proactive_suggestions(
        self, map_data: Dict[str, Any], analysis: Dict[str, Any]
    ) -> List[OptimizationSuggestion]:
        """Generate proactive suggestions (not from validation issues)."""
        import uuid

        suggestions = []

        # Check weapon variety
        weapons = map_data.get("weapons", [])
        weapon_types = set(w.get("type") for w in weapons)

        if len(weapon_types) < 3:
            suggestions.append(
                OptimizationSuggestion(
                    suggestion_id=str(uuid.uuid4()),
                    issue_type="weapon_variety",
                    description="Limited weapon variety",
                    suggestion="Add sniper rifle and explosive to weapon mix",
                    cost_credits=5,
                    impact="balance",
                    priority="medium",
                )
            )

        # Check healing coverage
        healing = map_data.get("healing", [])
        if len(healing) < 3:
            suggestions.append(
                OptimizationSuggestion(
                    suggestion_id=str(uuid.uuid4()),
                    issue_type="healing_coverage",
                    description="Insufficient healing items on map",
                    suggestion="Add more med kits and shields throughout the map",
                    cost_credits=2,
                    impact="balance",
                    priority="medium",
                )
            )

        # Check prop count
        props = map_data.get("props", [])
        if len(props) < 5:
            suggestions.append(
                OptimizationSuggestion(
                    suggestion_id=str(uuid.uuid4()),
                    issue_type="prop_coverage",
                    description="Low prop count - minimal cover",
                    suggestion="Add defensive structures and cover pieces",
                    cost_credits=3,
                    impact="playability",
                    priority="high",
                )
            )

        # Check team balance (prop distribution)
        if len(weapons) % 2 != 0:
            suggestions.append(
                OptimizationSuggestion(
                    suggestion_id=str(uuid.uuid4()),
                    issue_type="odd_weapon_count",
                    description="Odd number of weapons - teams won't have equal resources",
                    suggestion="Add or remove one weapon to balance teams",
                    cost_credits=3,
                    impact="balance",
                    priority="high",
                )
            )

        return suggestions

    def get_quick_wins(
        self, suggestions: List[OptimizationSuggestion], budget_credits: int
    ) -> List[OptimizationSuggestion]:
        """Get suggestions that fit within a credit budget (quick wins)."""
        affordable = []
        total = 0

        # Sort by cost (cheapest first) within priority
        by_priority = {}
        for s in suggestions:
            if s.priority not in by_priority:
                by_priority[s.priority] = []
            by_priority[s.priority].append(s)

        for priority_level in ["critical", "high", "medium", "low"]:
            if priority_level in by_priority:
                by_priority[priority_level].sort(key=lambda x: x.cost_credits)

                for suggestion in by_priority[priority_level]:
                    if total + suggestion.cost_credits <= budget_credits:
                        affordable.append(suggestion)
                        total += suggestion.cost_credits

        return affordable

    def estimate_cost_to_fix_all(
        self, suggestions: List[OptimizationSuggestion]
    ) -> int:
        """Get total cost to implement all suggestions."""
        return sum(s.cost_credits for s in suggestions)

    def summarize_suggestions(
        self, suggestions: List[OptimizationSuggestion]
    ) -> Dict[str, Any]:
        """Create a summary of suggestions for UI display."""
        by_priority = {}
        total_cost = 0

        for suggestion in suggestions:
            if suggestion.priority not in by_priority:
                by_priority[suggestion.priority] = []
            by_priority[suggestion.priority].append(suggestion)
            total_cost += suggestion.cost_credits

        return {
            "total_suggestions": len(suggestions),
            "total_cost": total_cost,
            "by_priority": {
                priority: {
                    "count": len(by_priority.get(priority, [])),
                    "cost": sum(
                        s.cost_credits for s in by_priority.get(priority, [])
                    ),
                    "items": [
                        {
                            "id": s.suggestion_id,
                            "issue": s.description,
                            "suggestion": s.suggestion,
                            "cost": s.cost_credits,
                            "impact": s.impact,
                        }
                        for s in by_priority.get(priority, [])
                    ],
                }
                for priority in ["critical", "high", "medium", "low"]
            },
        }
