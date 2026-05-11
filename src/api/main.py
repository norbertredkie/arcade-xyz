"""
Arcade.XYZ v2 API

Fortnite Map Creator Platform
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import logging

# Import modules
from ..editor import Map, MapBuilder, PropType, Vector3, Rotation
from ..optimizer import MapValidator
from ..earnings import CreatorFundEarnings
from ..fortnite import EpicGamesClient, FortniteCreativeAPI

# Setup
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Arcade.XYZ API",
    description="Fortnite Map Creator Platform",
    version="2.0.0",
    docs_url="/docs",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (in production, use database)
maps_db: Dict[str, Map] = {}
earnings_tracker = CreatorFundEarnings()
epic_client = EpicGamesClient()
validator = MapValidator()


# ============================================================================
# Schemas
# ============================================================================


class PropCreate(BaseModel):
    """Create prop request."""
    asset_id: str
    name: str
    prop_type: str
    position: Dict[str, float]
    rotation: Optional[Dict[str, float]] = None
    scale: Optional[Dict[str, float]] = None


class SpawnPointCreate(BaseModel):
    """Create spawn point request."""
    position: Dict[str, float]
    team: Optional[str] = None


class MapCreate(BaseModel):
    """Create map request."""
    title: str
    description: str


class MapUpdate(BaseModel):
    """Update map request."""
    title: Optional[str] = None
    description: Optional[str] = None


# ============================================================================
# Health & Auth
# ============================================================================


@app.get("/")
async def root():
    """API status."""
    return JSONResponse({"status": "🎮 Arcade.XYZ API v2.0.0 ready"})


@app.get("/health")
async def health():
    """Health check."""
    return JSONResponse({
        "status": "healthy",
        "version": "2.0.0",
        "environment": os.getenv("ENV", "development"),
    })


@app.get("/auth/epic/authorize")
async def get_epic_authorize_url(state: str):
    """Get Epic Games OAuth authorization URL."""
    try:
        auth_url = await epic_client.get_authorization_url(state)
        return JSONResponse({"authorization_url": auth_url})
    except Exception as e:
        logger.error(f"OAuth error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/epic/callback")
async def epic_callback(code: str, state: str):
    """Handle Epic Games OAuth callback."""
    try:
        token_response = await epic_client.exchange_code_for_token(code)
        # In production: store token in session/database
        return JSONResponse({
            "access_token": token_response.get("access_token"),
            "expires_in": token_response.get("expires_in"),
        })
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Map Editor Routes
# ============================================================================


@app.post("/maps")
async def create_map(req: MapCreate, creator_id: str):
    """Create new map."""
    try:
        builder = MapBuilder(req.title, req.description, creator_id)
        map_obj = builder.build()
        maps_db[map_obj.id] = map_obj

        return JSONResponse({
            "map_id": map_obj.id,
            "title": map_obj.title,
            "creator_id": map_obj.creator_id,
        })
    except Exception as e:
        logger.error(f"Map creation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/maps/{map_id}")
async def get_map(map_id: str):
    """Get map by ID."""
    if map_id not in maps_db:
        raise HTTPException(status_code=404, detail="Map not found")

    map_obj = maps_db[map_id]
    return JSONResponse(map_obj.to_dict())


@app.post("/maps/{map_id}/props")
async def add_prop_to_map(map_id: str, prop: PropCreate):
    """Add prop to map."""
    if map_id not in maps_db:
        raise HTTPException(status_code=404, detail="Map not found")

    try:
        map_obj = maps_db[map_id]
        position = Vector3(**prop.position)
        rotation = Rotation(**prop.rotation) if prop.rotation else Rotation()

        map_obj.add_prop(
            PropType(prop.prop_type),
            prop.asset_id,
            prop.name,
            position,
            rotation,
        )

        return JSONResponse({"success": True, "prop_count": len(map_obj.props)})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/maps/{map_id}/spawn-points")
async def add_spawn_point(map_id: str, spawn: SpawnPointCreate):
    """Add spawn point to map."""
    if map_id not in maps_db:
        raise HTTPException(status_code=404, detail="Map not found")

    try:
        map_obj = maps_db[map_id]
        position = Vector3(**spawn.position)
        map_obj.add_spawn_point(position, spawn.team)

        return JSONResponse({
            "success": True,
            "spawn_count": len(map_obj.spawn_points),
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Validation & Optimization
# ============================================================================


@app.post("/maps/{map_id}/validate")
async def validate_map(map_id: str):
    """Validate map against Fortnite specs."""
    if map_id not in maps_db:
        raise HTTPException(status_code=404, detail="Map not found")

    map_obj = maps_db[map_id]
    report = validator.validate(map_obj.to_dict())

    return JSONResponse(report)


# ============================================================================
# Publishing
# ============================================================================


@app.post("/maps/{map_id}/publish")
async def publish_map(map_id: str, access_token: str):
    """Publish map to Fortnite Creative."""
    if map_id not in maps_db:
        raise HTTPException(status_code=404, detail="Map not found")

    try:
        map_obj = maps_db[map_id]

        # First validate
        validation = validator.validate(map_obj.to_dict())
        if not validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail=f"Map validation failed: {validation['issues']}",
            )

        # Publish to Fortnite
        fortnite_api = FortniteCreativeAPI(access_token)
        result = await fortnite_api.publish_map(
            map_data=map_obj.to_dict(),
            creator_account_id=map_obj.creator_id,
            map_title=map_obj.title,
            map_description=map_obj.description,
        )

        return JSONResponse({
            "success": True,
            "map_id": map_id,
            "published_at": result.get("published_at"),
        })
    except Exception as e:
        logger.error(f"Publish error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Earnings Dashboard
# ============================================================================


@app.get("/earnings/creator/{creator_id}")
async def get_creator_earnings(creator_id: str):
    """Get creator earnings summary."""
    return JSONResponse(earnings_tracker.get_creator_total_earnings(creator_id))


@app.get("/earnings/map/{map_id}")
async def get_map_earnings(map_id: str):
    """Get earnings for specific map."""
    return JSONResponse(earnings_tracker.get_map_earnings(map_id))


@app.get("/earnings/leaderboard")
async def get_leaderboard(limit: int = 100):
    """Get top earners leaderboard."""
    return JSONResponse({"leaderboard": earnings_tracker.get_leaderboard(limit)})


@app.post("/earnings/record")
async def record_earning(
    creator_id: str,
    map_id: str,
    source: str,
    amount_usd: float,
):
    """Record earning (called by metrics service)."""
    import uuid

    earning = earnings_tracker.record_earning(
        earning_id=str(uuid.uuid4()),
        creator_id=creator_id,
        map_id=map_id,
        source=source,
        amount_usd=amount_usd,
    )

    return JSONResponse(earning.to_dict())


@app.post("/earnings/payout")
async def request_payout(
    creator_id: str,
    stripe_account_id: str,
):
    """Request payout (requires minimum earnings)."""
    creator_data = earnings_tracker.get_creator_total_earnings(creator_id)

    if not creator_data["ready_for_payout"]:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum $100 required. Current: ${creator_data['verified_earnings']}",
        )

    import uuid
    import stripe

    # Process payout via Stripe
    try:
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        payout = stripe.Payout.create(
            amount=int(creator_data["verified_earnings"] * 100),  # cents
            currency="usd",
            destination=stripe_account_id,
        )

        payout_record = earnings_tracker.process_payout(
            payout_id=str(uuid.uuid4()),
            creator_id=creator_id,
            amount_usd=creator_data["verified_earnings"],
            stripe_payout_id=payout.id,
        )

        return JSONResponse(payout_record)
    except Exception as e:
        logger.error(f"Payout error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Error Handlers
# ============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
