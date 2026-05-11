# Credits System Documentation

Arcade.XYZ v3 uses a **Clash of Clans-style credits economy** to monetize map optimizations.

## Overview

Users get a small monthly credit allowance (plan-dependent) and must purchase additional credits or upgrade their plan to optimize maps.

**Why it works:**
- Users generate basic maps for free (via AI)
- Each optimization costs credits → fast burndown
- Forced to upgrade or buy packs → revenue
- Creates FOMO ("I need to buy more credits!")

---

## Plans & Monthly Allowances

| Plan | Cost | Monthly Credits | Daily Bonus | Best For |
|------|------|-----------------|-------------|----------|
| **Free** | Free | 10 | — | Exploring, learning |
| **Pro** | $19/mo | 100 | — | Casual creators |
| **Studio** | $99/mo | 500 | +50/day | Teams, professional |

**Free users:** Almost worthless (10 credits only covers 1-2 optimizations)
**Studio users:** Can claim 50 bonus credits daily → 500 + (50 × 30) = 2000 credits/month

---

## Action Costs

Each map optimization costs credits:

```
- Add/move prop: 2 credits
- Relocate spawn point: 3 credits
- Weapon rebalance: 5 credits
- Healing item adjustment: 2 credits
- Accept AI suggestion: 3 credits
- Full map redesign: 25 credits
```

**Typical user journey:**
1. Generate map from prompt: **Free** (AI cost is our burden)
2. Get optimization suggestions: **Free** (showing what needs work)
3. Accept 1st suggestion (e.g., weapon balance): **5 credits** (balance: 100 → 95 if Pro)
4. Accept 2nd suggestion (spawn spacing): **3 credits** (balance: 95 → 92)
5. Accept 3rd suggestion (add healing): **2 credits** (balance: 92 → 90)
6. All 3 suggestions cost **10 credits** → Pro user is at 90

Users **burn through credits fast** → forced to upgrade.

---

## Credit Packs (One-Time Purchases)

Always available for impulse purchases:

```
- $9.99 → 50 credits ($0.20 per credit)
- $24.99 → 150 credits ($0.17 per credit)
- $49.99 → 500 credits ($0.10 per credit)
- $99.99 → 1500 credits ($0.07 per credit)
```

**Strategy:** Show packs when user runs out of credits during optimization.

---

## Implementation

### Backend (Python)

```python
from src.credits import CreditsTracker, CREDIT_COSTS

tracker = CreditsTracker()

# Create user (free plan by default)
user = tracker.create_user("user_123")

# Check balance
user = tracker.get_user("user_123")
print(f"Balance: {user.current_balance} credits")

# Deduct credits for an action
success, message, balance = tracker.deduct_credits(
    user_id="user_123",
    action="add_prop",
    map_id="map_456"
)

if success:
    print(f"✨ {message} | New balance: {balance}")
else:
    print(f"❌ {message}")

# Upgrade plan
success, msg, user = tracker.upgrade_plan("user_123", "pro")

# Claim daily bonus (Studio only)
success, msg, balance = tracker.claim_daily_bonus("user_123")
```

### API Endpoints

**Get user credits:**
```
GET /credits/user?user_id=user_123

Response:
{
  "current_balance": 95,
  "plan_type": "pro",
  "plan_name": "Pro",
  "plan_expires": "2025-06-11T...",
  "daily_bonus_available": false
}
```

**Deduct credits for action:**
```
POST /maps/{map_id}/optimize?user_id=user_123

Body:
{
  "action": "add_prop",
  "prop_id": "prop_456"
}

Response:
{
  "success": true,
  "message": "✨ Prop added",
  "new_balance": 93
}
```

**Upgrade plan:**
```
POST /subscription/upgrade?user_id=user_123

Body:
{
  "plan_type": "pro"
}

Response:
{
  "success": true,
  "plan_type": "pro",
  "current_balance": 150,
  "plan_expires": "2025-06-11T..."
}
```

**Claim daily bonus:**
```
POST /credits/claim-daily-bonus?user_id=user_123

Response:
{
  "success": true,
  "message": "🎁 +50 credits",
  "new_balance": 550
}
```

---

## Database Schema (Supabase)

### users_credits
```sql
CREATE TABLE users_credits (
  user_id UUID PRIMARY KEY,
  current_balance INTEGER DEFAULT 10,
  plan_type VARCHAR(20) DEFAULT 'free',  -- free, pro, studio
  plan_expires TIMESTAMP DEFAULT NOW() + 30 days,
  total_earned INTEGER DEFAULT 0,  -- lifetime
  total_spent INTEGER DEFAULT 0,   -- lifetime
  daily_bonus_claimed BOOLEAN DEFAULT false,
  daily_bonus_claimed_at TIMESTAMP,
  last_transaction TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### credit_transactions
```sql
CREATE TABLE credit_transactions (
  transaction_id UUID PRIMARY KEY,
  user_id UUID REFERENCES users_credits,
  amount INTEGER,  -- positive = credit, negative = debit
  type VARCHAR(50),  -- plan_initial, action_cost, purchase_pack, refund, etc.
  description VARCHAR(255),
  map_id UUID,
  timestamp TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW()
);
```

### credit_purchases
```sql
CREATE TABLE credit_purchases (
  purchase_id UUID PRIMARY KEY,
  user_id UUID REFERENCES users_credits,
  pack_amount INTEGER,  -- 50, 150, 500, 1500
  pack_cost INTEGER,    -- in cents
  stripe_payment_intent VARCHAR(255),
  status VARCHAR(20),   -- pending, completed, failed, refunded
  created_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP,
  refunded_at TIMESTAMP
);
```

---

## Monetization Strategy

**Revenue Model:**

1. **Subscriptions** (MRR)
   - 500 active users × $25 avg plan = $12,500/mo baseline
   - 20% on Pro ($19/mo) = $1,900/mo
   - 5% on Studio ($99/mo) = $2,475/mo
   - **Total: ~$4,300/mo from subscriptions**

2. **Credit Packs** (Impulse Purchases)
   - 30% of users buy packs
   - Average $15 per purchase
   - 500 users × 30% × $15 = $2,250/mo
   - **Total: ~$2,250/mo from packs**

3. **Total Potential:** **$6,550+/mo**

**Profitability:**
- Costs: OpenAI API (~$0.10 per map generation) + infrastructure
- 500 maps/month × $0.10 = $50 in AI costs
- Margin: **99% (before other operational costs)**

---

## User Psychology

**Why users spend:**

1. **Immediate gratification** - Suggestions appear right away
2. **FOMO** - "Everyone else is optimizing, I'm falling behind"
3. **Sunk cost** - Already invested time in map, might as well optimize
4. **Small costs** - 2-5 credits feels cheap, but adds up
5. **Progress bars** - Showing "you need 5 more credits" tempts spending

**Retention:**

- Users who spend credits come back (sunk cost effect)
- Daily bonuses keep Studio users engaged
- Leaderboard creates competition

---

## Edge Cases & Moderation

**Refunds:**
- User accidentally spent credits → `tracker.refund_transaction(txn_id, reason)`
- Logs entry for manual review

**Negative Balance Prevention:**
- Check balance before every deduction
- Return `(False, "Insufficient credits")` if needed

**Plan Expiry:**
- Check `user.plan_expires` daily
- Auto-downgrade to free if expired and no renewal
- Send email reminder before expiry

**Fraud Detection:**
- Monitor for unusual spending patterns
- Flag accounts buying many packs in short time
- Integrate with Stripe's fraud tools

---

## Future Enhancements

1. **Seasonal Bonuses** - Double credits during events
2. **Referral Rewards** - Earn credits by inviting friends
3. **Creator Fund** - Earn credits when maps played (reverse model)
4. **Team Pools** - Shared credit pool for Studio users
5. **Price Discrimination** - Higher costs for popular creators (Clash does this)

---

## Testing

Run tests:
```bash
pytest tests/test_credits.py -v
```

---

**Last Updated:** May 2025
**Version:** 3.0.0
