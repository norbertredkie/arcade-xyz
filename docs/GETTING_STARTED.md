# Getting Started with Arcade.XYZ v2

## Quick Setup (5 minutes)

### 1. Prerequisites

- Python 3.10+ (check with `python --version`)
- Node.js 18+ (check with `node --version`)
- Git
- Epic Games Developer account
- Stripe account (sandbox OK for testing)

### 2. Clone & Install

```bash
# Clone
git clone <repo>
cd arcade-xyz

# Backend setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup (optional for API-only development)
cd frontend
npm install
```

### 3. Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Epic Games OAuth (from https://www.epicgames.com/account/connections)
EPIC_GAMES_CLIENT_ID=your_client_id
EPIC_GAMES_CLIENT_SECRET=your_client_secret

# Fortnite Creator API (from Epic Games Console)
FORTNITE_API_KEY=your_api_key

# Database (from Supabase)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key

# Payments (from Stripe)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_test_...

# AI (from Anthropic)
ANTHROPIC_API_KEY=sk-ant-...

# JWT signing
JWT_SECRET=your-super-secret-key-min-32-chars

# Callback URL
CALLBACK_URL=http://localhost:3000/auth/epic/callback
```

### 4. Run Backend

```bash
# Activate venv
source venv/bin/activate

# Start API server
python -m uvicorn src.api.main:app --reload

# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 5. Run Frontend (Optional)

In a new terminal:

```bash
cd frontend
npm run dev

# Available at http://localhost:3000
```

---

## First Steps: Create Your First Map

### Via API (cURL)

```bash
# 1. Get Epic Games OAuth URL
curl http://localhost:8000/auth/epic/authorize?state=test123

# 2. Manually log in via returned URL, get code from redirect
# (In production, browser handles this)

# 3. Create a map
curl -X POST http://localhost:8000/maps \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Map",
    "description": "Learning Arcade.XYZ"
  }' \
  -G -d "creator_id=user123"

# Response:
# {
#   "map_id": "abc123...",
#   "title": "My First Map",
#   "creator_id": "user123"
# }

# 4. Add a prop
curl -X POST http://localhost:8000/maps/abc123.../props \
  -H "Content-Type: application/json" \
  -d '{
    "asset_id": "fortnite.building.wood_wall",
    "name": "Wood Wall",
    "prop_type": "building",
    "position": {
      "x": 100,
      "y": 100,
      "z": 0
    }
  }'

# 5. Add spawn points
curl -X POST http://localhost:8000/maps/abc123.../spawn-points \
  -H "Content-Type: application/json" \
  -d '{
    "position": {
      "x": 0,
      "y": 0,
      "z": 100
    },
    "team": "red"
  }'

# 6. Validate map
curl -X POST http://localhost:8000/maps/abc123.../validate

# Response shows any issues and suggestions

# 7. Publish to Fortnite
curl -X POST http://localhost:8000/maps/abc123.../publish \
  -H "Content-Type: application/json" \
  -d '{
    "access_token": "epic_access_token_here"
  }'
```

### Via Frontend UI

_Coming soon: React component walkthrough_

---

## Understanding the Data Model

### Map Structure

Every map is a JSON object:

```json
{
  "id": "map-uuid",
  "title": "My Awesome Map",
  "description": "Battle Royale for 4 players",
  "creator_id": "creator-uuid",
  "props": [
    {
      "id": "prop-uuid",
      "asset_id": "fortnite.building.wood_wall",
      "name": "Wood Wall",
      "type": "building",
      "position": { "x": 100, "y": 100, "z": 0 },
      "rotation": { "pitch": 0, "yaw": 0, "roll": 0 },
      "scale": { "x": 1, "y": 1, "z": 1 },
      "metadata": {}
    }
  ],
  "spawn_points": [
    {
      "id": "spawn-uuid",
      "position": { "x": 0, "y": 0, "z": 100 },
      "team": "red",
      "max_players": 1
    }
  ],
  "metadata": {
    "version": "2.0.0",
    "grid_size": 50,
    "bounds": {
      "min": { "x": -10000, "y": -10000, "z": 0 },
      "max": { "x": 10000, "y": 10000, "z": 3000 }
    }
  }
}
```

### Prop Types

Available `prop_type` values:

| Type | Description | Example |
|------|-------------|---------|
| `building` | Structures | Wall, floor, ramp |
| `weapon` | Guns & items | AR, Shotgun, Med Kit |
| `vehicle` | Vehicles | Helicopters |
| `terrain` | Landscape | Grass, water, rock |
| `trap` | Damage hazards | Spike trap, lava |
| `decoration` | Visual only | Trees, rocks |
| `spawn_point` | Player spawns | Shown separately |
| `item_box` | Loot containers | Chest, supply drop |

---

## Validation & Specs

### Running Validation

```bash
curl -X POST http://localhost:8000/maps/abc123.../validate
```

**Response Example (with issues):**

```json
{
  "valid": false,
  "error_count": 2,
  "warning_count": 1,
  "issues": [
    {
      "severity": "error",
      "code": "INSUFFICIENT_SPAWNS",
      "message": "Only 1 spawn points; minimum is 2",
      "suggestion": "Add more spawn points for team/deathmatch modes"
    },
    {
      "severity": "error",
      "code": "NO_WEAPONS",
      "message": "Map has no weapon spawns",
      "suggestion": "Add weapon spawns to combat areas"
    },
    {
      "severity": "warning",
      "code": "HIGH_POLY_COUNT",
      "message": "Estimated 500000 polys may exceed limit",
      "suggestion": "Remove or simplify props"
    }
  ]
}
```

### Fortnite Specs

**Hard Limits:**
- Max 10,000 props
- ~500,000 polygon count
- World bounds: X/Y [-10K, +10K], Z [0, 3K]

**Gameplay Minimums:**
- ≥2 spawn points
- ≥1 weapon spawn
- Weapons spaced 100+ units apart

---

## Publishing Maps

### Prerequisites

1. You have a Fortnite Creator Fund account
2. Your map passed validation
3. You have a valid Epic Games access token

### Publishing Flow

```bash
# 1. Get your Epic Games access token (from OAuth callback)
access_token="..."

# 2. Publish
curl -X POST http://localhost:8000/maps/abc123.../publish \
  -H "Content-Type: application/json" \
  -d '{"access_token": "'$access_token'"}'

# 3. Response:
# {
#   "success": true,
#   "map_id": "abc123...",
#   "published_at": "2025-01-15T10:30:00Z"
# }
```

After publishing, your map is live in Fortnite Creative mode!

---

## Earnings & Payouts

### Tracking Earnings

Each time someone plays your map:

```bash
# Called automatically by Epic's metrics service
curl -X POST http://localhost:8000/earnings/record \
  -G \
  -d "creator_id=user123" \
  -d "map_id=map_abc123" \
  -d "source=plays" \
  -d "amount_usd=0.25"
```

### Checking Your Earnings

```bash
curl http://localhost:8000/earnings/creator/user123

# Response:
# {
#   "creator_id": "user123",
#   "verified_earnings": 250.00,
#   "pending_earnings": 50.00,
#   "paid_earnings": 500.00,
#   "total_earnings": 800.00,
#   "ready_for_payout": true
# }
```

### Requesting a Payout

Minimum: $100 verified earnings

```bash
curl -X POST http://localhost:8000/earnings/payout \
  -G \
  -d "creator_id=user123" \
  -d "stripe_account_id=acct_stripe_id"

# Response:
# {
#   "payout_id": "payout_uuid",
#   "creator_id": "user123",
#   "amount_usd": 250.00,
#   "stripe_payout_id": "po_...",
#   "timestamp": "2025-01-15T11:00:00Z",
#   "status": "completed"
# }
```

---

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test

```bash
# Test map editor
pytest tests/test_editor.py -v

# Test validator
pytest tests/test_validator.py -v

# Test earnings
pytest tests/test_earnings.py -v
```

### Test Coverage

```bash
pytest tests/ --cov=src
```

---

## Troubleshooting

### "Connection refused" at http://localhost:8000

Make sure backend is running:
```bash
python -m uvicorn src.api.main:app --reload
```

### "Epic Games token exchange failed"

- Check `EPIC_GAMES_CLIENT_ID` and `EPIC_GAMES_CLIENT_SECRET` are correct
- Ensure `CALLBACK_URL` matches your registered redirect URI in Epic Games Console

### "Map validation failed: OUT_OF_BOUNDS"

Props are outside world limits. Valid range:
- X: -10,000 to 10,000
- Y: -10,000 to 10,000
- Z: 0 to 3,000

### "Minimum $100 required for payout"

Need more earnings! Keep creating popular maps. Each 1,000 plays = ~$0.25.

---

## Next Steps

- [Read the Architecture](./ARCHITECTURE.md)
- [View API Documentation](http://localhost:8000/docs)
- [Check out examples](../examples/)
- [Join the Discord community](https://discord.gg/arcade-xyz)

---

**Happy map building! 🎮**
