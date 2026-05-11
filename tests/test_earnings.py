"""Tests for earnings tracker."""

import pytest
from src.earnings import CreatorFundEarnings, EarningsStatus


def test_record_earning():
    """Test recording earning."""
    tracker = CreatorFundEarnings()
    earning = tracker.record_earning(
        earning_id="earn123",
        creator_id="creator1",
        map_id="map1",
        source="plays",
        amount_usd=5.0,
    )

    assert earning.creator_id == "creator1"
    assert earning.amount_usd == 5.0
    assert earning.status == EarningsStatus.PENDING


def test_calculate_plays_earnings():
    """Test play earnings calculation."""
    tracker = CreatorFundEarnings()
    earnings = tracker.calculate_plays_earnings(10000)

    # 10000 / 1000 * 0.25 = 2.5
    assert earnings == 2.5


def test_calculate_download_earnings():
    """Test download earnings calculation."""
    tracker = CreatorFundEarnings()
    earnings = tracker.calculate_download_earnings(1000)

    # 1000 / 100 * 0.50 = 5.0
    assert earnings == 5.0


def test_marketplace_split():
    """Test marketplace revenue split."""
    tracker = CreatorFundEarnings()
    creator_share, pbs_share = tracker.calculate_marketplace_split(100.0)

    assert creator_share == 85.0
    assert pbs_share == 15.0


def test_creator_total_earnings():
    """Test getting creator total earnings."""
    tracker = CreatorFundEarnings()

    # Add earnings
    tracker.record_earning("e1", "creator1", "map1", "plays", 50.0)
    tracker.record_earning("e2", "creator1", "map1", "plays", 30.0)

    totals = tracker.get_creator_total_earnings("creator1")

    assert totals["total_earnings"] == 80.0
    assert totals["pending_earnings"] == 80.0


def test_leaderboard():
    """Test leaderboard generation."""
    tracker = CreatorFundEarnings()

    tracker.record_earning("e1", "creator1", "map1", "plays", 100.0)
    tracker.record_earning("e2", "creator2", "map2", "plays", 50.0)
    tracker.record_earning("e3", "creator3", "map3", "plays", 75.0)

    leaderboard = tracker.get_leaderboard(limit=3)

    assert len(leaderboard) == 3
    assert leaderboard[0]["creator_id"] == "creator1"
    assert leaderboard[0]["rank"] == 1
    assert leaderboard[0]["total_earnings"] == 100.0


def test_payout_eligibility():
    """Test minimum payout eligibility."""
    tracker = CreatorFundEarnings()

    # Creator with low earnings
    tracker.record_earning("e1", "creator1", "map1", "plays", 50.0)
    totals = tracker.get_creator_total_earnings("creator1")
    assert totals["ready_for_payout"] == False

    # Creator with high earnings
    tracker.record_earning("e2", "creator2", "map2", "plays", 100.0)
    totals = tracker.get_creator_total_earnings("creator2")
    assert totals["ready_for_payout"] == True


def test_mark_earnings_verified():
    """Test marking earnings as verified."""
    tracker = CreatorFundEarnings()

    tracker.record_earning("e1", "creator1", "map1", "plays", 100.0)
    tracker.mark_earnings_verified("creator1")

    totals = tracker.get_creator_total_earnings("creator1")
    assert totals["verified_earnings"] == 100.0
    assert totals["pending_earnings"] == 0.0
