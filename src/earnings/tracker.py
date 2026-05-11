"""
Creator Fund Earnings Tracker

Manages earnings from Fortnite Creator Fund, calculates PBS commission, and tracks payouts.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum


class EarningsStatus(str, Enum):
    """Earnings status."""
    PENDING = "pending"
    VERIFIED = "verified"
    PAID = "paid"


@dataclass
class EarningRecord:
    """Single earning record."""
    id: str
    creator_id: str
    map_id: str
    source: str  # "plays", "downloads", "marketplace"
    amount_usd: float
    timestamp: datetime
    status: EarningsStatus = EarningsStatus.PENDING

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "creator_id": self.creator_id,
            "map_id": self.map_id,
            "source": self.source,
            "amount_usd": round(amount_usd, 2),
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value,
        }


class CreatorFundEarnings:
    """Manages Creator Fund payouts and tracking."""

    # Earning rates
    EARNINGS_PER_1000_PLAYS = 0.25  # USD per 1000 plays
    EARNINGS_PER_100_DOWNLOADS = 0.50  # USD per 100 downloads
    MARKETPLACE_CREATOR_SHARE = 0.85  # Creator keeps 85%, PBS takes 15%

    # Payout settings
    MINIMUM_PAYOUT = 100.0  # USD minimum before payout
    PAYOUT_FREQUENCY_DAYS = 30

    def __init__(self):
        self.earnings: List[EarningRecord] = []
        self.payouts: Dict[str, List[EarningRecord]] = {}

    def record_earning(
        self,
        earning_id: str,
        creator_id: str,
        map_id: str,
        source: str,
        amount_usd: float,
    ) -> EarningRecord:
        """Record a single earning."""
        record = EarningRecord(
            id=earning_id,
            creator_id=creator_id,
            map_id=map_id,
            source=source,
            amount_usd=amount_usd,
            timestamp=datetime.utcnow(),
            status=EarningsStatus.PENDING,
        )
        self.earnings.append(record)
        return record

    def calculate_plays_earnings(self, play_count: int) -> float:
        """Calculate earnings from play count."""
        return (play_count / 1000) * self.EARNINGS_PER_1000_PLAYS

    def calculate_download_earnings(self, download_count: int) -> float:
        """Calculate earnings from downloads."""
        return (download_count / 100) * self.EARNINGS_PER_100_DOWNLOADS

    def calculate_marketplace_split(self, sale_amount_usd: float) -> tuple:
        """
        Split marketplace sale between creator and PBS.
        
        Returns: (creator_share, pbs_share)
        """
        creator_share = sale_amount_usd * self.MARKETPLACE_CREATOR_SHARE
        pbs_share = sale_amount_usd - creator_share
        return (creator_share, pbs_share)

    def get_creator_total_earnings(self, creator_id: str) -> Dict[str, Any]:
        """Get total earnings for creator."""
        creator_earnings = [e for e in self.earnings if e.creator_id == creator_id]
        
        verified = sum(
            e.amount_usd for e in creator_earnings if e.status == EarningsStatus.VERIFIED
        )
        pending = sum(
            e.amount_usd for e in creator_earnings if e.status == EarningsStatus.PENDING
        )
        paid = sum(
            e.amount_usd for e in creator_earnings if e.status == EarningsStatus.PAID
        )

        return {
            "creator_id": creator_id,
            "verified_earnings": round(verified, 2),
            "pending_earnings": round(pending, 2),
            "paid_earnings": round(paid, 2),
            "total_earnings": round(verified + pending + paid, 2),
            "ready_for_payout": verified >= self.MINIMUM_PAYOUT,
        }

    def get_map_earnings(self, map_id: str) -> Dict[str, Any]:
        """Get earnings breakdown by map."""
        map_earnings = [e for e in self.earnings if e.map_id == map_id]

        by_source = {}
        for earning in map_earnings:
            if earning.source not in by_source:
                by_source[earning.source] = 0
            by_source[earning.source] += earning.amount_usd

        return {
            "map_id": map_id,
            "total_earnings": round(sum(e.amount_usd for e in map_earnings), 2),
            "by_source": {k: round(v, 2) for k, v in by_source.items()},
            "earnings_count": len(map_earnings),
        }

    def get_leaderboard(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get top earners leaderboard."""
        creator_totals = {}

        for earning in self.earnings:
            if earning.creator_id not in creator_totals:
                creator_totals[earning.creator_id] = 0
            creator_totals[earning.creator_id] += earning.amount_usd

        sorted_creators = sorted(
            creator_totals.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        leaderboard = []
        for rank, (creator_id, total) in enumerate(sorted_creators[:limit], 1):
            leaderboard.append({
                "rank": rank,
                "creator_id": creator_id,
                "total_earnings": round(total, 2),
            })

        return leaderboard

    def mark_earnings_verified(self, creator_id: str) -> int:
        """Mark pending earnings as verified (monthly reconciliation)."""
        updated = 0
        for earning in self.earnings:
            if (
                earning.creator_id == creator_id
                and earning.status == EarningsStatus.PENDING
            ):
                earning.status = EarningsStatus.VERIFIED
                updated += 1
        return updated

    def process_payout(
        self,
        payout_id: str,
        creator_id: str,
        amount_usd: float,
        stripe_payout_id: str,
    ) -> Dict[str, Any]:
        """Process payout to creator."""
        if creator_id not in self.payouts:
            self.payouts[creator_id] = []

        # Mark verified earnings as paid
        paid_count = 0
        for earning in self.earnings:
            if (
                earning.creator_id == creator_id
                and earning.status == EarningsStatus.VERIFIED
                and paid_count < (amount_usd * 1000)  # Rough approximation
            ):
                earning.status = EarningsStatus.PAID
                paid_count += 1

        payout_record = {
            "payout_id": payout_id,
            "creator_id": creator_id,
            "amount_usd": round(amount_usd, 2),
            "stripe_payout_id": stripe_payout_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed",
        }

        self.payouts[creator_id].append(payout_record)

        return payout_record

    def estimate_payout_date(self, creator_id: str) -> Optional[datetime]:
        """Estimate when creator can request payout."""
        creator_data = self.get_creator_total_earnings(creator_id)

        if not creator_data["ready_for_payout"]:
            return None

        # Estimate next payout in ~30 days
        return datetime.utcnow() + timedelta(days=self.PAYOUT_FREQUENCY_DAYS)
