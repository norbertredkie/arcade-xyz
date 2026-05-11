# Arcade.XYZ v2 Architecture

## Overview

Arcade.XYZ is a **Fortnite-focused map creation platform** for Epic Games Creative mode. Creators design maps using a visual editor, optimize them against Fortnite specs, publish to Creative, and earn from Fortnite Creator Fund.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (Next.js + React)                 │
│         - Map Editor UI (drag-drop builder)                  │
│         - Creator Dashboard (earnings, analytics)             │
│         - Marketplace (asset trading)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼──────────────────────────────────────┐
│                    FastAPI Backend                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ API Routes                                           │  │
│  │  - Map CRUD                                          │  │
│  │  - Prop management                                   │  │
│  │  - Validation & optimization                         │  │
│  │  - Publishing                                        │  │
│  │  - Earnings dashboard                                │  │
│  └──────────────────────────────────────────────────────┘  │
│                       │                                       │
│  ┌────────────────────┼───────────────────┐                 │
│  │                    │                   │                 │
│  ▼                    ▼                   ▼                 │
│ Editor          Optimizer           Fortnite API            │
│ - Map builder   - Validation        - Epic OAuth            │
│ - Props         - Specs check       - Publishing            │
│ - Serialization - Suggestions       - Stats                 │
│                                                              │
│  ┌────────────────────┬───────────────────┐                │
│  │                    │                   │                │
│  ▼                    ▼                   ▼                │
│ Earnings        Marketplace        Auth                    │
│ - Creator Fund  - Asset trading    - JWT                   │
│ - Payouts       - Revenue split    - CSRF                  │
│ - Leaderboard   - Reviews          - Rate limiting         │
└──────────────────────────────────────────────────────────────┘
                       │
       ┌───────────────┼────────────────┬──────────────┐
       │               │                │              │
       ▼               ▼                ▼              ▼
   Supabase       Epic Games API      Stripe      Anthropic
   (Database)     (Publishing)      (Payouts)    (Suggestions)
```

## Core Modules

### 1. **Editor** (`src/editor/`)

Map creation and manipulation.

**Classes:**
- `Map` - Fortnite map container
- `Prop` - Individual game object (building, weapon, etc.)
- `SpawnPoint` - Player spawn location
- `MapBuilder` - Fluent builder for map creation
- `Vector3`, `Rotation` - 3D math primitives

**Key Methods:**
```python
map = Map(id, title, description, creator_id)
map.add_prop(prop)
map.update_prop(prop_id, updates)
map.remove_prop(prop_id)
```

### 2. **Optimizer** (`src/optimizer/`)

Validation against Fortnite Creative specs.

**Classes:**
- `MapValidator` - Main validator engine
- `FortniteSpecs` - Specification constants
- `ValidationIssue` - Single validation result

**Constraints Enforced:**
- Max 10,000 props
- ~500K polygon count
- World bounds (-10K to +10K in X/Y, 0-3K in Z)
- Minimum 2 spawn points, max 100
- At least 1 weapon spawn
- Weapon spacing (100+ units apart)

### 3. **Fortnite API** (`src/fortnite/`)

Epic Games OAuth & Creative API integration.

**Classes:**
- `EpicGamesClient` - OAuth2 authentication
- `FortniteCreativeAPI` - Map publishing & tracking

**Key Endpoints:**
- `GET /auth/epic/authorize` - OAuth URL
- `POST /auth/epic/callback` - Token exchange
- `publish_map()` - Publish to Creative
- `get_map_stats()` - Fetch play data
- `validate_map_specs()` - Pre-publish validation

### 4. **Earnings** (`src/earnings/`)

Creator Fund earnings & payouts.

**Classes:**
- `CreatorFundEarnings` - Earnings tracker
- `EarningRecord` - Single earning entry

**Rates:**
- Plays: $0.25 per 1,000 plays
- Downloads: $0.50 per 100 downloads
- Marketplace: 85% creator, 15% PBS

**Minimums:**
- $100 before payout eligible

### 5. **API Routes** (`src/api/main.py`)

FastAPI application with all HTTP endpoints.

**Route Groups:**
1. **Health** - `/`, `/health`
2. **Auth** - `/auth/epic/*`
3. **Maps** - `/maps` (CRUD)
4. **Props** - `/maps/{id}/props` (management)
5. **Validation** - `/maps/{id}/validate`
6. **Publishing** - `/maps/{id}/publish`
7. **Earnings** - `/earnings/*`

## Data Flow

### Creating & Publishing a Map

```
Creator → Frontend UI
    ↓
Creates props (drag-drop)
Adds spawn points
    ↓
API: POST /maps/{id}/props
API: POST /maps/{id}/spawn-points
    ↓
Backend: MapBuilder serializes
    ↓
Creator clicks "Validate"
API: POST /maps/{id}/validate
    ↓
Backend: MapValidator checks specs
Returns: Issues + suggestions
    ↓
Creator fixes issues
    ↓
Creator clicks "Publish"
API: POST /maps/{id}/publish (access_token)
    ↓
Backend: Final validation
Backend: FortniteCreativeAPI.publish_map()
    ↓
Epic Games: Creates Fortnite Creative map
    ↓
Response: map_id, published_at
Creator → Dashboard (shows published)
```

### Earning Tracking

```
Player plays map on Fortnite → Epic's metrics service
    ↓
Daily: POST /earnings/record (creator_id, map_id, plays, amount)
    ↓
Backend: EarningRecord created (PENDING status)
    ↓
Monthly: mark_earnings_verified() called
    ↓
Creator: Sees verified earnings in dashboard
    ↓
Creator requests payout (if ≥$100)
    ↓
Backend: Stripe payout processed
    ↓
Creator: Funds in account (1-2 business days)
```

## Authentication

### OAuth2 (Epic Games)

**Flow:**
1. User clicks "Login with Epic"
2. Frontend redirects to `/auth/epic/authorize?state=...`
3. User logs into Epic Games & approves scope
4. Epic redirects to `/auth/epic/callback?code=...&state=...`
5. Backend exchanges code for access_token + refresh_token
6. Frontend stores JWT in session
7. All API calls include JWT in `Authorization: Bearer <token>`

### JWT

**Payload:**
```json
{
  "sub": "creator_id",
  "email": "creator@example.com",
  "account_id": "epic_account_id",
  "iat": 1234567890,
  "exp": 1234654290
}
```

**Signature:** HS256 with `JWT_SECRET` env var

## Database Schema (Supabase)

```
creators
├── id (UUID)
├── email
├── epic_account_id
├── epic_access_token
├── epic_refresh_token
├── stripe_account_id
└── created_at

maps
├── id (UUID)
├── creator_id (FK)
├── title
├── description
├── data (JSONB - serialized Map object)
├── published (boolean)
├── fortnite_map_id
├── created_at
└── updated_at

earnings
├── id (UUID)
├── creator_id (FK)
├── map_id (FK)
├── source (plays|downloads|marketplace)
├── amount_usd (decimal)
├── status (pending|verified|paid)
├── timestamp
└── created_at

payouts
├── id (UUID)
├── creator_id (FK)
├── amount_usd (decimal)
├── stripe_payout_id
├── status (completed|pending)
└── timestamp
```

## Deployment

### Prerequisites
- Python 3.10+
- PostgreSQL (Supabase)
- Stripe account
- Epic Games Developer Console (OAuth app)

### Environment Variables
```
ENV=production
EPIC_GAMES_CLIENT_ID=...
EPIC_GAMES_CLIENT_SECRET=...
FORTNITE_API_KEY=...
SUPABASE_URL=...
SUPABASE_KEY=...
STRIPE_SECRET_KEY=...
STRIPE_WEBHOOK_SECRET=...
ANTHROPIC_API_KEY=...
JWT_SECRET=...
CALLBACK_URL=https://arcade.xyz/auth/epic/callback
```

### Running
```bash
# Backend
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Frontend (separate repo)
npm run dev
```

## Security

1. **OAuth2** - Secure Epic Games authentication
2. **JWT** - Session management
3. **CSRF** - Anti-forgery tokens on forms
4. **Rate Limiting** - 5 req/sec per user
5. **Webhooks** - Stripe webhook signature verification
6. **CORS** - Restricted to arcade.xyz domain
7. **HTTPS** - All endpoints encrypted

## Performance Considerations

### Caching
- Map validation results cached for 5 minutes
- Creator earnings cached for 1 hour
- Fortnite spec constants cached in memory

### Async/Await
- All I/O operations are async (Epic API, Stripe, Supabase)
- Non-blocking request handling
- Connection pooling to databases

### Limits
- Max map size: 10,000 props (50MB serialized)
- Max API request body: 100MB
- Request timeout: 30 seconds
- Session TTL: 24 hours

## Testing

```bash
# Run all tests
pytest tests/ -v

# Coverage report
pytest tests/ --cov=src

# Specific test file
pytest tests/test_validator.py -v
```

## Monitoring & Logs

- CloudWatch logs for API errors
- Sentry for exception tracking
- Stripe event logs for payment issues
- Supabase query logs for database performance

## Future Enhancements

1. **Real-time Collaboration** - WebSocket support for multi-creator editing
2. **AI Asset Suggestions** - Anthropic Claude for prop placement
3. **Map Templates** - Pre-built map templates for quick start
4. **Custom Skins** - Creator marketplace for cosmetics
5. **Live Streaming** - Streaming overlay integration
6. **Mobile App** - iOS/Android companion app
