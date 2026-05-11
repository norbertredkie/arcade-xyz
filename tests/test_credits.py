"""
Tests for credits system
"""

import pytest
from src.credits import CreditsTracker, CREDIT_COSTS, PLAN_TYPES


@pytest.fixture
def tracker():
    """Create fresh tracker for each test."""
    return CreditsTracker()


def test_create_user_free_plan(tracker):
    """Test creating a new free user."""
    user = tracker.create_user("user_123", "free")

    assert user.user_id == "user_123"
    assert user.plan_type == "free"
    assert user.current_balance == PLAN_TYPES["free"]["monthly_credits"]
    assert user.total_earned == PLAN_TYPES["free"]["monthly_credits"]


def test_create_user_pro_plan(tracker):
    """Test creating a pro user."""
    user = tracker.create_user("user_456", "pro")

    assert user.plan_type == "pro"
    assert user.current_balance == PLAN_TYPES["pro"]["monthly_credits"]


def test_deduct_credits_success(tracker):
    """Test deducting credits for an action."""
    user = tracker.create_user("user_123", "pro")  # 100 credits
    initial_balance = user.current_balance

    success, msg, balance = tracker.deduct_credits(
        "user_123", "add_prop", "map_1"
    )

    assert success is True
    assert balance == initial_balance - CREDIT_COSTS["add_prop"]
    assert "✨" in msg


def test_deduct_credits_insufficient(tracker):
    """Test deducting when user has insufficient credits."""
    user = tracker.create_user("user_123", "free")  # 10 credits
    cost = CREDIT_COSTS["full_redesign"]  # 25 credits

    success, msg, balance = tracker.deduct_credits(
        "user_123", "full_redesign", "map_1"
    )

    assert success is False
    assert "Insufficient" in msg
    assert balance == PLAN_TYPES["free"]["monthly_credits"]  # Unchanged


def test_upgrade_plan(tracker):
    """Test upgrading subscription plan."""
    user = tracker.create_user("user_123", "free")
    old_balance = user.current_balance

    success, msg, user = tracker.upgrade_plan("user_123", "pro")

    assert success is True
    assert user.plan_type == "pro"
    assert user.current_balance > old_balance  # Got bonus credits


def test_daily_bonus_studio_plan(tracker):
    """Test claiming daily bonus on Studio plan."""
    user = tracker.create_user("user_123", "studio")
    old_balance = user.current_balance

    success, msg, balance = tracker.claim_daily_bonus("user_123")

    assert success is True
    assert "🎁" in msg
    assert balance == old_balance + 50


def test_daily_bonus_free_plan_fails(tracker):
    """Test that free users can't claim daily bonus."""
    tracker.create_user("user_123", "free")

    success, msg, balance = tracker.claim_daily_bonus("user_123")

    assert success is False
    assert "Studio plan" in msg


def test_daily_bonus_once_per_day(tracker):
    """Test that bonus can only be claimed once per day."""
    tracker.create_user("user_123", "studio")

    # Claim once
    success1, _, balance1 = tracker.claim_daily_bonus("user_123")
    assert success1 is True

    # Try to claim again
    success2, msg2, balance2 = tracker.claim_daily_bonus("user_123")
    assert success2 is False
    assert "Already claimed" in msg2


def test_transaction_history(tracker):
    """Test getting transaction history."""
    tracker.create_user("user_123", "pro")
    tracker.deduct_credits("user_123", "add_prop", "map_1")
    tracker.deduct_credits("user_123", "add_prop", "map_1")

    history = tracker.get_transaction_history("user_123", limit=10)

    assert len(history) > 0
    # Should have initial grant + 2 deductions
    assert any(t.type == "plan_initial" for t in history)
    assert sum(1 for t in history if t.type == "action_cost") == 2


def test_leaderboard(tracker):
    """Test leaderboard generation."""
    # Create multiple users
    tracker.create_user("user_1", "studio")  # 500 credits
    tracker.create_user("user_2", "pro")  # 100 credits
    tracker.create_user("user_3", "free")  # 10 credits

    leaderboard = tracker.get_leaderboard(limit=100)

    assert len(leaderboard) == 3
    assert leaderboard[0]["user_id"] == "user_1"  # Highest
    assert leaderboard[0]["total_earned"] == 500


def test_refund_transaction(tracker):
    """Test refunding a transaction."""
    tracker.create_user("user_123", "pro")
    _, _, balance_before = tracker.deduct_credits("user_123", "add_prop", "map_1")

    # Get transaction ID
    history = tracker.get_transaction_history("user_123", limit=100)
    debit_txn = [t for t in history if t.type == "action_cost"][0]

    # Refund it
    success, msg = tracker.refund_transaction(debit_txn.transaction_id, "test refund")

    assert success is True
    user = tracker.get_user("user_123")
    # Balance should be back to initial after refund
    assert user.current_balance == PLAN_TYPES["pro"]["monthly_credits"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
