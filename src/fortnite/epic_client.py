"""
Fortnite Creative API Client

Handles OAuth2 authentication with Epic Games and map publishing to Fortnite.
"""

import os
import json
import aiohttp
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt

EPIC_OAUTH_URL = "https://www.epicgames.com/id/oauth/authorize"
EPIC_TOKEN_URL = "https://api.epicgames.com/oauth/token"
FORTNITE_API_BASE = "https://fortnite-api.com/v2"


class EpicGamesClient:
    """OAuth2 client for Epic Games authentication."""

    def __init__(self):
        self.client_id = os.getenv("EPIC_GAMES_CLIENT_ID")
        self.client_secret = os.getenv("EPIC_GAMES_CLIENT_SECRET")
        self.redirect_uri = os.getenv("CALLBACK_URL", "https://arcade.xyz/auth/epic/callback")
        self.base_url = EPIC_TOKEN_URL

    async def get_authorization_url(self, state: str) -> str:
        """Generate OAuth authorization URL."""
        return (
            f"{EPIC_OAUTH_URL}?"
            f"client_id={self.client_id}&"
            f"response_type=code&"
            f"scope=openid offline_access&"
            f"redirect_uri={self.redirect_uri}&"
            f"state={state}"
        )

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
            }

            async with session.post(
                self.base_url,
                auth=auth,
                data=data,
            ) as resp:
                if resp.status != 200:
                    raise ValueError(f"Epic Games token exchange failed: {await resp.text()}")
                return await resp.json()

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh expired access token."""
        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            }

            async with session.post(
                self.base_url,
                auth=auth,
                data=data,
            ) as resp:
                if resp.status != 200:
                    raise ValueError(f"Token refresh failed: {await resp.text()}")
                return await resp.json()


class FortniteCreativeAPI:
    """Fortnite Creative mode API client."""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.api_key = os.getenv("FORTNITE_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "X-API-Key": self.api_key,
        }

    async def publish_map(
        self,
        map_data: Dict[str, Any],
        creator_account_id: str,
        map_title: str,
        map_description: str,
    ) -> Dict[str, Any]:
        """Publish map to Fortnite Creative mode."""
        async with aiohttp.ClientSession() as session:
            payload = {
                "map": map_data,
                "creator_account_id": creator_account_id,
                "title": map_title,
                "description": map_description,
                "published_at": datetime.utcnow().isoformat(),
            }

            async with session.post(
                f"{FORTNITE_API_BASE}/creative/maps/publish",
                headers=self.headers,
                json=payload,
            ) as resp:
                if resp.status != 201:
                    raise ValueError(f"Map publish failed: {await resp.text()}")
                return await resp.json()

    async def get_map_stats(self, map_id: str) -> Dict[str, Any]:
        """Get map play/download statistics."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{FORTNITE_API_BASE}/creative/maps/{map_id}/stats",
                headers=self.headers,
            ) as resp:
                if resp.status != 200:
                    raise ValueError(f"Failed to get map stats: {await resp.text()}")
                return await resp.json()

    async def list_creator_maps(self, creator_account_id: str) -> list:
        """List all maps published by creator."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{FORTNITE_API_BASE}/creative/creators/{creator_account_id}/maps",
                headers=self.headers,
            ) as resp:
                if resp.status != 200:
                    raise ValueError(f"Failed to list maps: {await resp.text()}")
                return (await resp.json()).get("maps", [])

    async def validate_map_specs(self, map_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate map against Fortnite Creative specs."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{FORTNITE_API_BASE}/creative/validate",
                headers=self.headers,
                json=map_data,
            ) as resp:
                if resp.status != 200:
                    raise ValueError(f"Map validation failed: {await resp.text()}")
                return await resp.json()

    async def sync_marketplace_listing(
        self,
        map_id: str,
        list_on_marketplace: bool,
        price_v_bucks: int = 0,
    ) -> Dict[str, Any]:
        """Sync map to Fortnite Marketplace (if applicable)."""
        async with aiohttp.ClientSession() as session:
            payload = {
                "map_id": map_id,
                "list_on_marketplace": list_on_marketplace,
                "price_v_bucks": price_v_bucks,
            }

            async with session.patch(
                f"{FORTNITE_API_BASE}/creative/maps/{map_id}/marketplace",
                headers=self.headers,
                json=payload,
            ) as resp:
                if resp.status != 200:
                    raise ValueError(f"Marketplace sync failed: {await resp.text()}")
                return await resp.json()
