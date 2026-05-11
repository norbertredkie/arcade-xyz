# AI Map Generation Documentation

Arcade.XYZ v3 uses Claude AI to instantly generate complete, playable Fortnite maps from natural language prompts.

## Overview

**User says:** "Close quarters chaos with tight corridors"
**Claude returns:** Complete map with spawn points, weapons, healing, props, and geometry

**Result:** Playable map in ~30 seconds (basic but functional)

---

## How It Works

### Prompt Flow

```
User Input: "Sniper heaven"
    ↓
Claude Prompt (with system instructions)
    ↓
Claude returns JSON: {spawn_points, weapons, healing, props, bounds}
    ↓
System validates and saves map
    ↓
User can immediately optimize or play
```

### Example Prompts

Users describe what gameplay style they want:

1. **"Sniper heaven"**
   - Wide open areas
   - Tall buildings for positioning
   - Minimal close-range weapons
   - Long sightlines

2. **"Close quarters chaos"**
   - Tight corridors
   - Shotgun-heavy spawns
   - Short sightlines
   - Cover everywhere

3. **"Land grab 50v50"**
   - Large central area
   - Balanced team spawns
   - Mix of all weapon types
   - Defensive structures

4. **"Parkour paradise"**
   - Vertical movement
   - Jump pads
   - Ramps and slopes
   - Open rooftops

5. **"Tournament TDM"**
   - Small, balanced map
   - Equal resource access
   - Symmetrical design
   - Competitive flow

---

## API Integration

### Generate Map from Prompt

```bash
POST /maps/generate

Body:
{
  "prompt": "Close quarters chaos with tight corridors",
  "title": "Deathmatch Arena"  # optional
}

Headers:
- user_id: user_123

Response:
{
  "success": true,
  "map_id": "map_abc123",
  "title": "Deathmatch Arena",
  "ai_generated": true,
  "ai_prompt": "Close quarters chaos with tight corridors",
  "spawn_count": 8,
  "weapon_count": 12,
  "prop_count": 25,
  "healing_count": 6
}
```

### Get Generated Map

```bash
GET /maps/map_abc123

Response:
{
  "map_id": "map_abc123",
  "title": "Deathmatch Arena",
  "spawn_points": [
    {"x": -200, "y": 0, "z": 100, "team": "team_a"},
    {"x": 200, "y": 0, "z": 100, "team": "team_b"},
    ...
  ],
  "weapons": [
    {"type": "AR", "x": 0, "y": 0, "z": 150, "ammo": 120},
    {"type": "Shotgun", "x": -100, "y": -100, "z": 150, "ammo": 24},
    ...
  ],
  "healing": [
    {"type": "Small Shield", "x": 50, "y": 50, "z": 100},
    ...
  ],
  "props": [
    {"type": "Wall", "x": 0, "y": 200, "z": 100, "rotation": 0},
    ...
  ]
}
```

---

## Map JSON Structure

Generated maps follow this schema:

```json
{
  "title": "Map Name",
  "description": "What type of gameplay this is",
  "spawn_points": [
    {
      "x": 0,
      "y": 0,
      "z": 100,
      "team": "team_a"  // team_a or team_b
    }
  ],
  "weapons": [
    {
      "type": "AR",           // AR, Shotgun, Sniper, Explosive, etc.
      "x": 0,
      "y": 0,
      "z": 150,
      "ammo": 120             // Starting ammo
    }
  ],
  "healing": [
    {
      "type": "Small Shield", // Small Shield, Med Kit, Chug Jug, etc.
      "x": 0,
      "y": 0,
      "z": 100
    }
  ],
  "props": [
    {
      "type": "Wall",         // Defensive structure
      "x": 0,
      "y": 0,
      "z": 100,
      "rotation": 0
    }
  ],
  "bounds": {
    "x_min": -1000,
    "x_max": 1000,
    "y_min": -1000,
    "y_max": 1000
  }
}
```

---

## Claude System Prompt

The system prompt guides Claude to generate valid, playable maps:

```
You are an expert Fortnite Creative map designer. Generate complete, playable maps from user prompts.

Your job: Convert natural language descriptions into structured map JSON.

IMPORTANT: Return ONLY valid JSON (no markdown, no "```json", no commentary).

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
```

---

## Code Implementation

### Python Backend

```python
from src.ai import AIMapGenerator
import asyncio

generator = AIMapGenerator(api_key="sk-...")

async def main():
    # Generate map
    map_data = await generator.generate_map(
        prompt="Close quarters chaos with tight corridors"
    )
    
    print(f"✨ Generated: {map_data['title']}")
    print(f"  Spawns: {len(map_data['spawn_points'])}")
    print(f"  Weapons: {len(map_data['weapons'])}")
    print(f"  Props: {len(map_data['props'])}")

asyncio.run(main())
```

### Frontend (React/Next.js)

```typescript
// components/AIGenerator.tsx

export function AIMapGenerator() {
  const [prompt, setPrompt] = useState("");
  const [generating, setGenerating] = useState(false);

  async function handleGenerate() {
    setGenerating(true);
    
    const res = await fetch("/maps/generate", {
      method: "POST",
      body: JSON.stringify({ prompt }),
      headers: { "Content-Type": "application/json" }
    });
    
    const { map_id, title } = await res.json();
    
    // Navigate to editor
    router.push(`/editor/${map_id}`);
    setGenerating(false);
  }

  return (
    <div className="ai-generator">
      <h2>✨ Generate Map</h2>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Describe your ideal map..."
      />
      <button
        onClick={handleGenerate}
        disabled={generating}
      >
        {generating ? "⏳ Creating..." : "🚀 Generate Map"}
      </button>
    </div>
  );
}
```

---

## Quality & Limitations

### Strengths

✅ **Fast** - 30 seconds to playable map
✅ **Valid JSON** - Always returns valid structure
✅ **Balanced** - Respects team symmetry rules
✅ **Variety** - Different maps for different prompts
✅ **User-friendly** - No technical knowledge needed

### Limitations

⚠️ **Basic** - Maps are functional but not optimized
⚠️ **No advanced geometry** - Only standard Fortnite props
⚠️ **Repetitive** - May use similar layouts for similar prompts
⚠️ **No custom assets** - Can't import external props

**Solution:** Users optimize with AI suggestions (paid with credits)

---

## Optimization Flow

Maps are intentionally basic to encourage optimization:

```
Generate Map (AI)
    ↓ (Basic but playable)
    ↓
Analyze (System finds issues)
    ↓
Suggest (Show 5-10 improvement options)
    ↓ (Each costs 2-5 credits)
    ↓
Optimize (User clicks to apply)
    ↓ (Deduct credits, Claude improves map)
    ↓
Final Polished Map
```

---

## Prompt Engineering Tips

**What works well:**
- Specific game mode: "Team Deathmatch", "Capture the Flag"
- Playstyle: "Aggressive", "Campy", "Mobility-focused"
- Spatial style: "Tight corridors", "Open fields", "Vertical"
- Weapon emphasis: "Sniper-heavy", "Close quarters", "Balanced"

**What doesn't work:**
- Vague: "Cool map" (returns average)
- Too specific: "Place 47 AR spawns at exact coordinates" (Claude refuses)
- Story-based: "Medieval castle" (not Fortnite-relevant)

**Best practices:**
1. Start with game mode
2. Add playstyle/vibe
3. Mention key features
4. Be specific about resources (weapons, healing, cover)

**Example prompt formula:**
```
"{game_mode} map with {playstyle} gameplay. 
Features: {key features}. 
Weapons: {emphasis}.
Style: {spatial layout}."
```

**Real example:**
```
"Team Deathmatch with aggressive close-quarters gameplay.
Features: tight corridors, multiple levels, good cover.
Weapons: Shotgun and AR heavy, minimal sniper.
Style: compact urban setting."
```

---

## Error Handling

**Common issues:**

1. **Invalid JSON response**
   - Solution: Retry with same prompt (usually works)
   - Fallback: Return template map

2. **Unbalanced resources**
   - Solution: Claude respects rules, validate output
   - Fallback: Let users optimize

3. **Out of bounds props**
   - Solution: Validator catches and suggests fix
   - Cost: 2 credits to relocate

4. **Rate limits**
   - Solution: Queue requests, rate limit per user
   - Fallback: Show "waiting..." message

---

## Future Enhancements

1. **Custom props library** - Users upload custom assets
2. **Map variants** - Generate similar maps with variations
3. **Guided generation** - Step-by-step wizard instead of free text
4. **Coaching** - "This map needs more cover" suggestions
5. **Community templates** - Generate from popular layouts
6. **Iterative refinement** - User feedback loops improve generation

---

## Testing

```bash
# Test AI generator
python -m src.ai.map_generator

# Test API
curl -X POST http://localhost:8000/maps/generate \
  -H "Content-Type: application/json" \
  -H "user-id: test_user" \
  -d '{"prompt": "Close quarters chaos"}'
```

---

**Last Updated:** May 2025
**Version:** 3.0.0
