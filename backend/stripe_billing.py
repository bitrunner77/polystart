"""
PolyStart - Stripe Billing (Skeleton)
Pricing:
- Free: 3 follows, basic alerts
- Pro ($9.99/mo): Unlimited follows, auto-copy, advanced alerts

Note: Requires STRIPE_API_KEY environment variable
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import stripe
import os

router = APIRouter()

# Stripe configuration
stripe.api_key = os.environ.get("STRIPE_API_KEY")

PRICE_ID_PRO = os.environ.get("STRIPE_PRICE_ID", "price_xxx")

# Models
class CreateCheckoutRequest(BaseModel):
    price_id: str = PRICE_ID_PRO
    user_id: int

class CreateCheckoutResponse(BaseModel):
    checkout_url: str

@router.post("/create-checkout")
async def create_checkout_session(req: CreateCheckoutRequest):
    """Create Stripe checkout session"""
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": req.price_id, "quantity": 1}],
            mode="subscription",
            success_url="https://polystart.example.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://polystart.example.com/cancel",
            metadata={"user_id": req.user_id}
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(payload: dict, sig: str):
    """Handle Stripe webhooks"""
    # In production: verify signature with stripe.WebhookSignature
    event_type = payload.get("type")
    
    if event_type == "checkout.session.completed":
        # Grant pro access to user
        pass
    elif event_type == "customer.subscription.deleted":
        # Revoke pro access
        pass
    
    return {"status": "received"}

@router.get("/subscription/{user_id}")
async def get_subscription(user_id: int):
    """Get user's subscription status"""
    # In production: query database for subscription
    return {
        "user_id": user_id,
        "tier": "free",  # or "pro"
        "features": ["3 follows", "basic alerts"]
    }

# Pricing tiers
TIERS = {
    "free": {
        "price": 0,
        "features": [
            "Follow up to 3 traders",
            "Basic alerts (daily summary)",
            "Top 20 traders list"
        ]
    },
    "pro": {
        "price": 9.99,
        "features": [
            "Unlimited follows",
            "Real-time Telegram alerts",
            "Auto-copy (beta)",
            "Advanced analytics",
            "Priority support"
        ]
    }
}