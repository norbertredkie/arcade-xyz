"""
AI Map Generator - Claude generates maps from natural language prompts
"""

import json
import asyncio
from typing import Dict, Any, Optional
from anthropic import Anthropic
import logging

logger = logging.getLogger(__name__)

# Prompt template for Claude
SYSTEM_PROMPT = """You are an expert Fortnite Creative map designer. Generate complete, playable maps from user prompts.

Your job: Convert natural language descriptions into structured map JSON.

IMPORTANT: Return ONLY valid JSON (no markdown, no "```json", no commentary).

Map structure:
{
  "title": "Map name",
  "description": "What type of map",
  "spawn_points": [
    {"x": 0, "y": 0, "z": 100, "team": "team_a"},
    {"x": 500, "y": 0, "z": 100, "team": "team_b"}
  ],
  "weapons": [
    {"type": "AR", "x": 250, "y": 0, "z": 150, "ammo": 120},
    {"type": "Shotgun", "x": -250, "y": 0, "z": 150, "ammo": 24},
    {"type": "Sniper", "x": 0, "y": 500, "z": 200, "ammo": 6}
  ],
  "healing": [
    {"type": "Small Shield", "x": 100, "y": 100, "z": 100},
    {"type": "Med Kit", "x": -100, "y": -100, "z": 100}
  ],
  "props": [
    {"type": "Wall", "x": 0, "y": 250, "z": 100, "rotation": 0},
    {"type": "Building", "x": 200, "y": 200, "z": 100, "rotation": 45}
  ],
  "bounds": {"x_min": -1000, "x_max": 1000, "y_min": -1000, "y_max": 1000}
}

Rules:
1. Spawn points: 2-32 per team, balanced positions, no overlaps
2. Weapons: Mix of AR, shotgun, sniper, explosives
3. Healing: Scattered, especially in dangerous areas
4. Props: Natural cover, vertical variety, balance across map
5. Bounds: Standard Fortnite Creative bounds (-1000 to 1000)
6. Balance: Equal resources for both teams
7. Playability: Ensure spawn safety, weapon access, cover

Example prompt: "Close quarters chaos"
Expected: Tight corridors, shotgun-heavy, lots of close-range props, spawns near center

Generate a map that matches the user's intent. Be creative but ensure playability."""


class AIMapGenerator:
    """Generate Fortnite maps from natural language prompts using Claude AI."""

    def __init__(self, api_key: str):
        """Initialize Anthropic client."""
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"

    async def generate_map(self, prompt: str) -> Dict[str, Any]:
        """
        Generate a complete map from a natural language prompt.
        
        Args:
            prompt: User's map description (e.g., "Close quarters chaos")
            
        Returns:
            Generated map JSON structure
        """
        try:
            # Call Claude with streaming
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Generate a complete Fortnite Creative map matching this prompt:

"{prompt}"

Return ONLY valid JSON, no markdown or commentary."""
                    }
                ],
                system=SYSTEM_PROMPT,
            )

            # Extract response text
            response_text = response.content[0].text.strip()

            # Parse JSON
            map_data = json.loads(response_text)

            # Add metadata
            map_data["generated"] = True
            map_data["ai_prompt"] = prompt

            logger.info(f"✨ Generated map from prompt: {prompt}")
            return map_data

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Response text: {response_text[:500]}")
            raise ValueError(f"AI generated invalid JSON: {str(e)}")
        except Exception as e:
            logger.error(f"Map generation error: {e}")
            raise

    async def suggest_optimizations(
        self, map_data: Dict[str, Any], analysis: Dict[str, Any]
    ) -> list:
        """
        Suggest map optimizations based on analysis.
        
        Args:
            map_data: Current map structure
            analysis: Map validation analysis results
            
        Returns:
            List of optimization suggestions with credit costs
        """
        try:
            issues = analysis.get("issues", [])
            if not issues:
                return []

            # Build context from issues
            issues_text = "\n".join(
                [f"- {issue['type']}: {issue['message']}" for issue in issues]
            )

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": f"""You are a Fortnite map design expert. Analyze these map issues and suggest specific, actionable fixes.

Map title: {map_data.get('title', 'Untitled')}
Issues found:
{issues_text}

For EACH issue, suggest ONE specific fix. Return JSON array with this structure:
[
  {{
    "issue": "Issue description",
    "suggestion": "What to do (be specific)",
    "cost_credits": 2,
    "impact": "What improves (balance/playability/spacing)"
  }}
]

Return ONLY valid JSON array, no markdown."""
                    }
                ],
            )

            response_text = response.content[0].text.strip()
            suggestions = json.loads(response_text)

            logger.info(f"✨ Generated {len(suggestions)} optimization suggestions")
            return suggestions

        except Exception as e:
            logger.error(f"Optimization suggestion error: {e}")
            return []

    async def apply_optimization(
        self, map_data: Dict[str, Any], suggestion: str
    ) -> Dict[str, Any]:
        """
        Apply a specific optimization suggestion to a map.
        
        Args:
            map_data: Current map structure
            suggestion: Optimization suggestion text
            
        Returns:
            Updated map structure
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Update this Fortnite Creative map based on the optimization suggestion.

Current map:
{json.dumps(map_data, indent=2)}

Optimization to apply:
{suggestion}

Return the UPDATED map JSON only, no markdown or commentary."""
                    }
                ],
                system=SYSTEM_PROMPT,
            )

            response_text = response.content[0].text.strip()
            updated_map = json.loads(response_text)

            logger.info(f"✨ Applied optimization: {suggestion[:50]}")
            return updated_map

        except Exception as e:
            logger.error(f"Optimization application error: {e}")
            raise


if __name__ == "__main__":
    # Test
    import os

    async def test():
        generator = AIMapGenerator(api_key=os.getenv("ANTHROPIC_API_KEY"))

        # Test 1: Generate map
        print("🔄 Generating map...")
        map_data = await generator.generate_map("Close quarters chaos with tight corridors")
        print(f"✨ Generated map: {map_data['title']}")
        print(json.dumps(map_data, indent=2)[:500] + "...\n")

        # Test 2: Get suggestions
        print("🔄 Getting suggestions...")
        analysis = {
            "valid": False,
            "issues": [
                {"type": "weapon_balance", "message": "Shotgun spawns too far"},
                {"type": "spawn_spacing", "message": "Team spawns too close"},
            ],
        }
        suggestions = await generator.suggest_optimizations(map_data, analysis)
        print(f"✨ Got {len(suggestions)} suggestions:")
        for s in suggestions:
            print(f"  - {s['suggestion']} ({s['cost_credits']} credits)")

    asyncio.run(test())
