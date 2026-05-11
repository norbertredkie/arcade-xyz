"""
Arcade.XYZ v3 API - AI-Powered Map Creator with Credits System

NEW FEATURES:
- AI Map Generation from prompts
- Credits economy (Clash of Clans style)
- Optimization suggestions
- Stripe payment integration
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import logging
import asyncio

# Import core modules
from ..editor import Map, MapBuilder
from ..optimizer import MapValidator
from ..ai import AIMapGenerator, MapOptimizer
from ..credits import CreditsTracker, CREDIT_PACKS, PLAN_TYPES
from ..payments import StripePaymentHandler
from ..design_system import DESIGN_TOKENS

# Setup
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Arcade.XYZ API v3",
    description="AI-Powered Fortnite Map Creator with Credits Economy",
    version="3.0.0",
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

# Global instances
maps_db: Dict[str, Map] = {}
validator = MapValidator()
ai_generator = AIMapGenerator(api_key=os.getenv("ANTHROPIC_API_KEY"))
optimizer = MapOptimizer(validator=validator)
credits_tracker = CreditsTracker()
stripe_handler = StripePaymentHandler()


# ============================================================================
# SCHEMAS
# ============================================================================


class GenerateMapRequest(BaseModel):
    """Generate map from AI prompt."""

    prompt: str
    title: Optional[str] = None


class OptimizationRequest(BaseModel):
    """Request optimization suggestions for a map."""

    map_id: str


class ApplySuggestionRequest(BaseModel):
    """Apply an optimization suggestion."""

    map_id: str
    suggestion_id: str


class BuyCreditPackRequest(BaseModel):
    """Purchase credit pack."""

    pack_index: int  # 0-3, index into CREDIT_PACKS


class CreatePaymentIntentRequest(BaseModel):
    """Create Stripe payment intent."""

    pack_index: int


class ConfirmPaymentRequest(BaseModel):
    """Confirm payment and grant credits."""

    intent_id: str


class UpgradePlanRequest(BaseModel):
    """Upgrade user subscription plan."""

    plan_type: str  # "free", "pro", "studio"


# ============================================================================
# HEALTH & VERSION
# ============================================================================


@app.get("/")
async def root():
    """API status."""
    return JSONResponse({
        "status": "🎮 Arcade.XYZ v3.0.0 - AI Map Creator with Credits",
        "features": [
            "AI Map Generation",
            "Credits System",
            "Optimization Engine",
            "Stripe Payments",
        ],
    })


@app.get("/health")
async def health():
    """Health check."""
    return JSONResponse({
        "status": "healthy",
        "version": "3.0.0",
        "environment": os.getenv("ENV", "development"),
    })


@app.get("/design-tokens")
async def get_design_tokens():
    """Get Gen Z UI design tokens."""
    return JSONResponse(DESIGN_TOKENS)


# ============================================================================
# AI MAP GENERATION
# ============================================================================


@app.post("/maps/generate")
async def generate_map(req: GenerateMapRequest, user_id: str):
    """
    🚀 Generate a complete map from a natural language prompt.
    
    Example: "Close quarters chaos with tight corridors"
    """
    try:
        # Generate map using Claude
        logger.info(f"🚀 Generating map from prompt: {req.prompt}")
        map_data = await ai_generator.generate_map(req.prompt)

        # Create map object
        builder = MapBuilder(
            title=req.title or map_data.get("title", "AI Generated"),
            description=map_data.get("description", ""),
            creator_id=user_id,
        )
        map_obj = builder.build()

        # Update with AI-generated data
        map_obj.spawn_points = map_data.get("spawn_points", [])
        map_obj.weapons = map_data.get("weapons", [])
        map_obj.healing = map_data.get("healing", [])
        map_obj.props = map_data.get("props", [])

        maps_db[map_obj.id] = map_obj

        return JSONResponse({
            "success": True,
            "map_id": map_obj.id,
            "title": map_obj.title,
            "description": map_obj.description,
            "ai_generated": True,
            "ai_prompt": req.prompt,
            "spawn_count": len(map_obj.spawn_points),
            "weapon_count": len(map_obj.weapons),
            "prop_count": len(map_obj.props),
            "healing_count": len(map_obj.healing),
        })

    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# MAP MANAGEMENT
# ============================================================================


@app.get("/maps/{map_id}")
async def get_map(map_id: str):
    """Get map by ID."""
    if map_id not in maps_db:
        raise HTTPException(status_code=404, detail="Map not found")

    map_obj = maps_db[map_id]
    return JSONResponse({
        "map_id": map_obj.id,
        "title": map_obj.title,
        "description": map_obj.description,
        "creator_id": map_obj.creator_id,
        "spawn_points": map_obj.spawn_points,
        "weapons": map_obj.weapons,
        "healing": map_obj.healing,
        "props": map_obj.props,
    })


# ============================================================================
# OPTIMIZATION & SUGGESTIONS
# ============================================================================


@app.post("/maps/{map_id}/analyze")
async def analyze_map(map_id: str, user_id: str):
    """
    Analyze a map and get optimization suggestions.
    
    Shows what's wrong and how much credits each fix costs.
    """
    if map_id not in maps_db:
        raise HTTPException(status_code=404, detail="Map not found")

    try:
        map_obj = maps_db[map_id]
        map_data = {
            "title": map_obj.title,
            "spawn_points": map_obj.spawn_points,
            "weapons": map_obj.weapons,
            "healing": map_obj.healing,
            "props": map_obj.props,
        }

        # Get suggestions
        suggestions, analysis = optimizer.analyze_and_suggest(map_data)

        # Filter to affordable ones
        user = credits_tracker.get_user(user_id)
        affordable = optimizer.get_quick_wins(suggestions, user.current_balance)

        summary = optimizer.summarize_suggestions(suggestions)

        return JSONResponse({
            "map_id": map_id,
            "analysis_valid": analysis.get("valid", False),
            "total_issues": len(analysis.get("issues", [])),
            "suggestions_available": len(suggestions),
            "affordable_suggestions": len(affordable),
            "user_balance": user.current_balance,
            "cost_to_fix_all": optimizer.estimate_cost_to_fix_all(suggestions),
            "summary": summary,
            "suggestions": [
                {
                    "id": s.suggestion_id,
                    "issue": s.description,
                    "suggestion": s.suggestion,
                    "cost_credits": s.cost_credits,
                    "impact": s.impact,
                    "priority": s.priority,
                    "affordable": s.cost_credits <= user.current_balance,
                }
                for s in suggestions
            ],
        })

    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# CREDITS SYSTEM
# ============================================================================


@app.get("/credits/user")
async def get_user_credits(user_id: str):
    """Get user's credit state and subscription."""
    user = credits_tracker.get_user(user_id)

    return JSONResponse({
        "user_id": user_id,
        "current_balance": user.current_balance,
        "plan_type": user.plan_type,
        "plan_name": PLAN_TYPES[user.plan_type]["name"],
        "plan_expires": user.plan_expires.isoformat(),
        "total_earned": user.total_earned,
        "total_spent": user.total_spent,
        "daily_bonus_available": (
            user.plan_type == "studio"
            and not user.daily_bonus_claimed
        ),
    })


@app.post("/credits/claim-daily-bonus")
async def claim_daily_bonus(user_id: str):
    """Claim daily Studio bonus (50 credits/day)."""
    success, message, balance = credits_tracker.claim_daily_bonus(user_id)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return JSONResponse({
        "success": True,
        "message": message,
        "new_balance": balance,
    })


@app.get("/credits/transaction-history")
async def get_transaction_history(user_id: str, limit: int = 50):
    """Get user's credit transaction history."""
    transactions = credits_tracker.get_transaction_history(user_id, limit)

    return JSONResponse({
        "user_id": user_id,
        "transaction_count": len(transactions),
        "transactions": [t.to_dict() for t in transactions],
    })


@app.get("/credits/leaderboard")
async def get_leaderboard(limit: int = 100):
    """Get top creators by credits earned."""
    leaderboard = credits_tracker.get_leaderboard(limit)

    return JSONResponse({
        "rank_count": len(leaderboard),
        "leaderboard": leaderboard,
    })


# ============================================================================
# SUBSCRIPTIONS
# ============================================================================


@app.post("/subscription/upgrade")
async def upgrade_plan(req: UpgradePlanRequest, user_id: str):
    """Upgrade subscription plan."""
    success, message, user = credits_tracker.upgrade_plan(user_id, req.plan_type)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return JSONResponse({
        "success": True,
        "message": message,
        "plan_type": user.plan_type,
        "current_balance": user.current_balance,
        "plan_expires": user.plan_expires.isoformat(),
    })


# ============================================================================
# STRIPE PAYMENTS
# ============================================================================


@app.get("/credit-packs")
async def list_credit_packs():
    """List available credit packs for purchase."""
    return JSONResponse({
        "packs": [
            {
                "index": i,
                "amount": pack["amount"],
                "cost_cents": pack["cost"],
                "cost_usd": f"${pack['cost'] / 100:.2f}",
                "price_per_credit": f"${pack['cost'] / 100 / pack['amount']:.4f}",
                "badge": "🔥 Best Value" if i == 2 else "",
            }
            for i, pack in enumerate(CREDIT_PACKS)
        ],
    })


@app.post("/payments/create-intent")
async def create_payment_intent(
    req: CreatePaymentIntentRequest, user_id: str
):
    """
    Create Stripe PaymentIntent for credit pack purchase.
    
    Returns client_secret for frontend to use with Stripe.js
    """
    if req.pack_index < 0 or req.pack_index >= len(CREDIT_PACKS):
        raise HTTPException(status_code=400, detail="Invalid pack index")

    pack = CREDIT_PACKS[req.pack_index]

    try:
        intent_data = stripe_handler.create_payment_intent(
            user_id=user_id,
            amount_cents=pack["cost"],
            pack_amount=pack["amount"],
        )

        # Record in credits tracker
        credits_tracker.record_purchase(
            user_id=user_id,
            pack_amount=pack["amount"],
            pack_cost=pack["cost"],
            stripe_intent=intent_data["intent_id"],
        )

        return JSONResponse({
            "success": True,
            "intent_id": intent_data["intent_id"],
            "client_secret": intent_data["client_secret"],
            "amount_cents": intent_data["amount"],
            "amount_usd": f"${intent_data['amount'] / 100:.2f}",
            "credits_receiving": pack["amount"],
        })

    except Exception as e:
        logger.error(f"Payment intent error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/payments/confirm")
async def confirm_payment(req: ConfirmPaymentRequest, user_id: str):
    """
    Confirm a payment intent and grant credits.
    
    Call this after Stripe.js confirms the payment on the frontend.
    """
    try:
        success, message, intent_data = stripe_handler.confirm_payment(
            req.intent_id
        )

        if not success:
            raise HTTPException(status_code=400, detail=message)

        # Grant credits
        success, message = credits_tracker.complete_purchase(
            purchase_id=None  # TODO: store purchase_id properly
        )

        # Get updated user state
        user = credits_tracker.get_user(user_id)

        return JSONResponse({
            "success": True,
            "message": "✨ Credits added to your account!",
            "new_balance": user.current_balance,
            "user_id": user_id,
        })

    except Exception as e:
        logger.error(f"Payment confirmation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks (payment_intent.succeeded, etc.)."""
    body = await request.body()
    sig_header = request.headers.get("stripe-signature")

    valid, event = stripe_handler.verify_webhook_signature(body.decode(), sig_header)

    if not valid:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        result = stripe_handler.handle_payment_succeeded_webhook(
            intent["id"],
            intent["metadata"],
        )

        if result.get("success"):
            # Grant credits to user
            user_id = result["user_id"]
            pack_amount = result["pack_amount"]

            credits_tracker.record_transaction(
                user_id=user_id,
                amount=pack_amount,
                type="purchase_pack",
                description=f"Credit pack purchase ({pack_amount} credits)",
            )

            logger.info(f"✨ Webhook processed: {user_id} +{pack_amount} credits")

    return JSONResponse({"received": True})


# ============================================================================
# PRICING INFO
# ============================================================================


@app.get("/pricing")
async def get_pricing():
    """Get pricing information for plans and credit packs."""
    return JSONResponse({
        "plans": {
            plan_type: {
                "name": info["name"],
                "cost_usd": f"${info['cost'] / 100:.2f}" if info["cost"] > 0 else "Free",
                "monthly_credits": info["monthly_credits"],
                "daily_bonus": info["daily_bonus"],
                "description": (
                    "Explore and learn"
                    if plan_type == "free"
                    else "For casual creators"
                    if plan_type == "pro"
                    else "For studios and teams"
                ),
            }
            for plan_type, info in PLAN_TYPES.items()
        },
        "credit_costs": {
            "add_prop": 2,
            "relocate_spawn": 3,
            "weapon_rebalance": 5,
            "full_redesign": 25,
            "accept_suggestion": 3,
        },
        "credit_packs": [
            {
                "amount": pack["amount"],
                "cost": f"${pack['cost'] / 100:.2f}",
            }
            for pack in CREDIT_PACKS
        ],
    })


# ============================================================================
# ERROR HANDLERS
# ============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected errors."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
