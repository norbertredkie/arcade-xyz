# 🎮 Arcade.XYZ v2 - Fortnite Map Creator Platform

**Professional map builder for Fortnite Creative.** Creators design, optimize, publish, and earn from their maps on the Fortnite marketplace.

## ✨ Core Features

### 1. **Fortnite Map Editor**
- Drag-drop visual builder with Fortnite-native props
- Real-time preview & performance metrics
- Grid/snap system + terrain tools
- Weapon placement & spawn point management

### 2. **Optimization Engine**
- Validate against Epic Games Fortnite specs
- Poly count & memory limits enforcement
- Weapon balance analysis + spawn point audits
- Auto-suggestions for improvements

### 3. **Fortnite Creative API Integration**
- Epic Games authentication (OAuth2)
- Direct publish to Fortnite Creative mode
- Marketplace sync + play tracking
- Version control for maps

### 4. **Earnings Dashboard**
- Real-time Creator Fund earnings
- PBS revenue split (15% commission)
- Payout tracking & leaderboard
- Map analytics (plays, downloads, ratings)

### 5. **Creator Marketplace** (Secondary)
- Custom skins, props, cosmetics
- Peer-to-peer trading
- Revenue split between creators

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+ (frontend)
- Epic Games Developer Account
- Fortnite Creator Fund enrollment

### Installation

```bash
# Clone & setup
git clone <repo>
cd arcade-xyz
cp .env.example .env

# Fill .env with:
# EPIC_GAMES_CLIENT_ID=
# EPIC_GAMES_CLIENT_SECRET=
# FORTNITE_API_KEY=
# SUPABASE_URL=
# SUPABASE_KEY=
# STRIPE_SECRET_KEY=
# ANTHROPIC_API_KEY=

# Run
./deploy.sh
```

### Environment Variables

```
EPIC_GAMES_CLIENT_ID          # OAuth app ID (Epic Games Console)
EPIC_GAMES_CLIENT_SECRET      # OAuth app secret
FORTNITE_API_KEY              # Fortnite Creator API key
SUPABASE_URL                  # Database URL
SUPABASE_KEY                  # Database token
STRIPE_SECRET_KEY             # Payment processing
ANTHROPIC_API_KEY             # Claude AI (optional: asset suggestions)
JWT_SECRET                    # Session signing (auto-generated)
```

---

## 💰 Pricing & Revenue

| Plan | Monthly | Features |
|------|---------|----------|
| **Creator** | Free | Editor, 3 maps, basic stats |
| **Pro** | $19 | Unlimited maps, analytics, early marketplace |
| **Studio** | $99 | Team collaboration, API access, custom branding |

**PBS Commission:** 15% of all Creator Fund payouts

**Projected Revenue:** 500 active creators × $2-5/mo avg earnings × 15% = $1,500-3,750/mo

---

## 📂 Architecture

```
arcade-xyz/
├── src/
│   ├── api/                 # FastAPI routes
│   ├── editor/              # Map editor backend
│   ├── optimizer/           # Fortnite spec validation
│   ├── fortnite/            # Epic Games API client
│   ├── earnings/            # Creator Fund tracking
│   ├── marketplace/         # Asset trading system
│   ├── auth/                # OAuth2 + JWT
│   └── db/                  # Supabase ORM
├── frontend/                # Next.js + React
│   ├── pages/
│   ├── components/
│   ├── stores/              # Zustand state
│   └── styles/
├── tests/
├── docs/
└── deploy.sh
```

---

## 🛠️ Development

```bash
# Backend
cd src && python -m uvicorn api.main:app --reload

# Frontend
cd frontend && npm run dev

# Tests
pytest tests/ -v
```

---

## 📚 Documentation

- [Fortnite API Integration](./docs/fortnite-api.md)
- [Map Validation Specs](./docs/validation-specs.md)
- [Earnings Model](./docs/earnings.md)
- [Contributing Guide](./CONTRIBUTING.md)

---

## 🔐 Security

- OAuth2 with Epic Games
- JWT + CSRF protection
- Rate limiting (5 req/sec per user)
- PCI compliance (Stripe)
- Webhook idempotency

---

## 📞 Support

- **Docs:** https://arcade.xyz/docs
- **Discord:** https://discord.gg/arcade-xyz
- **Email:** support@arcade.xyz

---

**v2.0.0** | Rebuilt for Fortnite Creative | © 2025 PBS
