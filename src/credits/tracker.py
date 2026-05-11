"""
Credit balance tracking and transaction management
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from .models import (
    CreditTransaction,
    UserCreditsState,
    CreditPurchase,
    SubscriptionChange,
    CREDIT_COSTS,
    PLAN_TYPES,
)

logger = logging.getLogger(__name__)


class CreditsTracker:
    """Track user credit balances, transactions, and plan subscriptions."""

    def __init__(self):
        """Initialize tracker (in-memory for now, swap with DB)."""
        self.users: Dict[str, UserCreditsState] = {}
        self.transactions: Dict[str, CreditTransaction] = {}
        self.purchases: Dict[str, CreditPurchase] = {}
        self.subscriptions: Dict[str, SubscriptionChange] = {}

    def create_user(
        self, user_id: str, plan_type: str = "free"
    ) -> UserCreditsState:
        """Create new user with initial credits."""
        plan_info = PLAN_TYPES[plan_type]

        user = UserCreditsState(
            user_id=user_id,
            current_balance=plan_info["monthly_credits"],
            plan_type=plan_type,
            plan_expires=datetime.utcnow() + timedelta(days=30),
            total_earned=plan_info["monthly_credits"],
            total_spent=0,
            daily_bonus_claimed=False,
        )

        self.users[user_id] = user

        # Record initial credit grant
        self.record_transaction(
            user_id=user_id,
            amount=plan_info["monthly_credits"],
            type="plan_initial",
            description=f"Initial {plan_type} plan credits",
        )

        logger.info(f"✨ Created user {user_id} on {plan_type} plan")
        return user

    def get_user(self, user_id: str) -> Optional[UserCreditsState]:
        """Get user's credit state."""
        if user_id not in self.users:
            return self.create_user(user_id, "free")
        return self.users[user_id]

    def record_transaction(
        self,
        user_id: str,
        amount: int,
        type: str,
        description: str,
        map_id: Optional[str] = None,
    ) -> CreditTransaction:
        """Record a credit transaction."""
        import uuid

        transaction = CreditTransaction(
            transaction_id=str(uuid.uuid4()),
            user_id=user_id,
            amount=amount,
            type=type,
            description=description,
            map_id=map_id,
        )

        self.transactions[transaction.transaction_id] = transaction

        # Update user balance
        user = self.get_user(user_id)
        user.current_balance += amount
        user.total_earned += max(0, amount)
        user.total_spent += max(0, -amount)
        user.last_transaction = datetime.utcnow()
        user.updated_at = datetime.utcnow()

        logger.info(
            f"💳 Transaction: {user_id} | {description} | {amount:+d} credits | "
            f"Balance: {user.current_balance}"
        )

        return transaction

    def deduct_credits(
        self, user_id: str, action: str, map_id: str
    ) -> Tuple[bool, str, int]:
        """
        Deduct credits for an action.
        
        Returns: (success, message, remaining_balance)
        """
        user = self.get_user(user_id)
        cost = CREDIT_COSTS.get(action, 0)

        if cost == 0:
            return False, f"Unknown action: {action}", user.current_balance

        if user.current_balance < cost:
            return (
                False,
                f"Insufficient credits. Need {cost}, have {user.current_balance}",
                user.current_balance,
            )

        # Deduct credits
        self.record_transaction(
            user_id=user_id,
            amount=-cost,
            type="action_cost",
            description=f"{action}",
            map_id=map_id,
        )

        return True, f"✨ {action} applied", user.current_balance

    def claim_daily_bonus(self, user_id: str) -> Tuple[bool, str, int]:
        """
        Claim daily bonus credits (Studio plan only).
        
        Returns: (success, message, new_balance)
        """
        user = self.get_user(user_id)

        if user.plan_type != "studio":
            return (
                False,
                "Daily bonus only available on Studio plan",
                user.current_balance,
            )

        if user.daily_bonus_claimed:
            # Check if claimed today
            if user.daily_bonus_claimed_at:
                if user.daily_bonus_claimed_at.date() == datetime.utcnow().date():
                    return (
                        False,
                        "Already claimed bonus today",
                        user.current_balance,
                    )

        # Award bonus
        bonus_amount = 50
        self.record_transaction(
            user_id=user_id,
            amount=bonus_amount,
            type="daily_bonus",
            description="Daily Studio bonus",
        )

        user.daily_bonus_claimed = True
        user.daily_bonus_claimed_at = datetime.utcnow()

        logger.info(f"🎁 Daily bonus claimed: {user_id} +{bonus_amount} credits")
        return True, f"🎁 +{bonus_amount} credits", user.current_balance

    def upgrade_plan(
        self, user_id: str, new_plan: str
    ) -> Tuple[bool, str, UserCreditsState]:
        """
        Upgrade user to new plan (and grant monthly credits).
        
        Returns: (success, message, updated_user)
        """
        user = self.get_user(user_id)

        if new_plan not in PLAN_TYPES:
            return False, f"Invalid plan: {new_plan}", user

        old_plan = user.plan_type
        plan_info = PLAN_TYPES[new_plan]

        # Record subscription change
        import uuid

        change = SubscriptionChange(
            change_id=str(uuid.uuid4()),
            user_id=user_id,
            from_plan=old_plan,
            to_plan=new_plan,
            from_cost=PLAN_TYPES[old_plan]["cost"],
            to_cost=plan_info["cost"],
        )
        self.subscriptions[change.change_id] = change

        # Update plan
        user.plan_type = new_plan
        user.plan_expires = datetime.utcnow() + timedelta(days=30)
        user.daily_bonus_claimed = False
        user.daily_bonus_claimed_at = None

        # Grant monthly credits (if upgrading from lower tier)
        old_monthly = PLAN_TYPES[old_plan]["monthly_credits"]
        new_monthly = plan_info["monthly_credits"]

        if new_monthly > old_monthly:
            bonus = new_monthly - old_monthly
            self.record_transaction(
                user_id=user_id,
                amount=bonus,
                type="plan_upgrade",
                description=f"Upgrade to {new_plan} plan",
            )

        logger.info(f"📈 Upgraded {user_id}: {old_plan} → {new_plan}")
        return True, f"Upgraded to {new_plan} plan", user

    def record_purchase(
        self, user_id: str, pack_amount: int, pack_cost: int, stripe_intent: str
    ) -> CreditPurchase:
        """Record a credit pack purchase."""
        import uuid

        purchase = CreditPurchase(
            purchase_id=str(uuid.uuid4()),
            user_id=user_id,
            pack_amount=pack_amount,
            pack_cost=pack_cost,
            stripe_payment_intent=stripe_intent,
            status="pending",
        )

        self.purchases[purchase.purchase_id] = purchase
        logger.info(
            f"💳 Purchase pending: {user_id} | {pack_amount} credits | ${pack_cost/100:.2f}"
        )

        return purchase

    def complete_purchase(self, purchase_id: str) -> Tuple[bool, str]:
        """Mark purchase as completed and grant credits."""
        if purchase_id not in self.purchases:
            return False, "Purchase not found"

        purchase = self.purchases[purchase_id]

        if purchase.status != "pending":
            return False, f"Purchase already {purchase.status}"

        # Mark completed
        purchase.status = "completed"
        purchase.completed_at = datetime.utcnow()

        # Grant credits
        self.record_transaction(
            user_id=purchase.user_id,
            amount=purchase.pack_amount,
            type="purchase_pack",
            description=f"Credit pack purchase ({purchase.pack_amount} credits)",
        )

        logger.info(f"✨ Purchase completed: {purchase.user_id} +{purchase.pack_amount}")
        return True, "Credits added to account"

    def get_transaction_history(
        self, user_id: str, limit: int = 50
    ) -> List[CreditTransaction]:
        """Get user's transaction history."""
        user_txns = [
            t for t in self.transactions.values() if t.user_id == user_id
        ]
        # Sort by timestamp, newest first
        user_txns.sort(key=lambda x: x.timestamp, reverse=True)
        return user_txns[:limit]

    def get_leaderboard(self, limit: int = 100) -> List[dict]:
        """Get top creators by total credits earned."""
        users_list = list(self.users.values())
        users_list.sort(key=lambda x: x.total_earned, reverse=True)

        return [
            {
                "rank": i + 1,
                "user_id": user.user_id,
                "total_earned": user.total_earned,
                "current_balance": user.current_balance,
                "plan_type": user.plan_type,
            }
            for i, user in enumerate(users_list[:limit])
        ]

    def refund_transaction(
        self, transaction_id: str, reason: str
    ) -> Tuple[bool, str]:
        """Refund a transaction by creating a reverse transaction."""
        if transaction_id not in self.transactions:
            return False, "Transaction not found"

        original = self.transactions[transaction_id]

        # Create reverse transaction
        reverse = self.record_transaction(
            user_id=original.user_id,
            amount=-original.amount,  # Reverse the amount
            type="refund",
            description=f"Refund: {original.description} ({reason})",
            map_id=original.map_id,
        )

        logger.info(f"↩️ Refunded transaction {transaction_id}: {reason}")
        return True, f"Refunded {abs(original.amount)} credits"
