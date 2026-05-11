"""
Credits system models and database schemas
"""

from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime
import uuid

# Credit costs for different actions
CREDIT_COSTS = {
    "add_prop": 2,
    "move_prop": 2,
    "relocate_spawn": 3,
    "weapon_rebalance": 5,
    "healing_adjustment": 2,
    "full_redesign": 25,
    "accept_suggestion": 3,
}

PLAN_TYPES = {
    "free": {
        "monthly_credits": 10,
        "daily_bonus": 0,
        "cost": 0,
        "name": "Free",
    },
    "pro": {
        "monthly_credits": 100,
        "daily_bonus": 0,
        "cost": 1999,  # cents
        "name": "Pro",
    },
    "studio": {
        "monthly_credits": 500,
        "daily_bonus": 50,
        "cost": 9900,  # cents
        "name": "Studio",
    },
}

CREDIT_PACKS = [
    {"amount": 50, "cost": 999},  # $9.99
    {"amount": 150, "cost": 2499},  # $24.99
    {"amount": 500, "cost": 4999},  # $49.99
    {"amount": 1500, "cost": 9999},  # $99.99
]


@dataclass
class CreditTransaction:
    """A single credit transaction (debit or credit)."""

    transaction_id: str
    user_id: str
    amount: int  # Positive = credit, Negative = debit
    type: str  # "plan_monthly", "purchase_pack", "action_cost", "bonus", etc.
    description: str
    map_id: Optional[str] = None
    timestamp: datetime = None
    related_transaction: Optional[str] = None  # For reversals/refunds

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    def to_dict(self):
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class UserCreditsState:
    """Current credit balance and subscription state for a user."""

    user_id: str
    current_balance: int  # Total available credits
    plan_type: str  # "free", "pro", "studio"
    plan_expires: datetime  # When current plan expires
    total_earned: int  # Lifetime credits earned
    total_spent: int  # Lifetime credits spent
    daily_bonus_claimed: bool  # Has user claimed today's bonus?
    daily_bonus_claimed_at: Optional[datetime] = None
    last_transaction: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

    def to_dict(self):
        """Convert to dictionary."""
        data = asdict(self)
        data["plan_expires"] = self.plan_expires.isoformat()
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        if self.daily_bonus_claimed_at:
            data["daily_bonus_claimed_at"] = self.daily_bonus_claimed_at.isoformat()
        return data


@dataclass
class CreditPurchase:
    """Credit pack purchase (Stripe integration)."""

    purchase_id: str
    user_id: str
    pack_amount: int  # How many credits
    pack_cost: int  # Cost in cents
    stripe_payment_intent: str
    status: str  # "pending", "completed", "failed", "refunded"
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

    def to_dict(self):
        """Convert to dictionary."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        if self.completed_at:
            data["completed_at"] = self.completed_at.isoformat()
        if self.refunded_at:
            data["refunded_at"] = self.refunded_at.isoformat()
        return data


@dataclass
class SubscriptionChange:
    """Record of a plan upgrade/downgrade."""

    change_id: str
    user_id: str
    from_plan: str
    to_plan: str
    from_cost: int  # Monthly cost in cents
    to_cost: int  # Monthly cost in cents
    created_at: datetime = None
    refund_issued: bool = False

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

    def to_dict(self):
        """Convert to dictionary."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        return data
