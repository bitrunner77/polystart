"""
PolyStart Backend - FastAPI + Real Polymarket API + User Management
Beginner-friendly Polymarket copy trading tool

Features:
- Real Polymarket leaderboard data
- User accounts with Telegram auth
- Follow/unfollow traders
- Rate limiting (free tier vs pro)
- Caching for API calls
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import requests
import secrets
import time
from datetime import datetime

# Import routers
from .search import router as search_router
from .analytics import router as analytics_router
from .notifications import router as notifications_router

app = FastAPI(title="PolyStart API")

# Include routers
app.include_router(search_router, prefix="/search", tags=["Search"])
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
app.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])

# CORS - allow Vercel and localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DB_FILE = 'polystart.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id TEXT UNIQUE,
        username TEXT,
        api_token TEXT UNIQUE,
        tier TEXT DEFAULT 'free',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS followed_traders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        trader_address TEXT,
        trader_name TEXT,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        UNIQUE(user_id, trader_address)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS trader_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        period TEXT,
        data TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()

init_db()

# Rate limiting
FREE_TIER_LIMIT = 100  # requests per hour
rate_limits = {}  # {token: (count, reset_time)}

def check_rate_limit(token: str) -> bool:
    if not token:
        return True  # No token, allow for now
    
    now = time.time()
    if token not in rate_limits:
        rate_limits[token] = [1, now + 3600]
        return True
    
    count, reset_time = rate_limits[token]
    if now > reset_time:
        rate_limits[token] = [1, now + 3600]
        return True
    
    if count >= FREE_TIER_LIMIT:
        return False
    
    rate_limits[token][0] += 1
    return True

# Models
class UserCreate(BaseModel):
    telegram_id: str
    username: str

class FollowRequest(BaseModel):
    trader_address: str
    trader_name: str = "Unknown"

class UnfollowRequest(BaseModel):
    trader_address: str

class TraderResponse(BaseModel):
    rank: str
    address: str
    username: str
    pnl: float
    vol: float
    verified: bool

# Polymarket API
POLYMARKET_API = "https://data-api.polymarket.com"

def get_leaderboard(category: str = "OVERALL", period: str = "MONTH", limit: int = 20, use_cache: bool = True) -> List[dict]:
    """Fetch top traders from Polymarket API with caching"""
    
    # Check cache first (5 min TTL)
    if use_cache:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            SELECT data, updated_at FROM trader_cache 
            WHERE category = ? AND period = ?
            AND datetime(updated_at) > datetime('now', '-5 minutes')
        """, (category, period))
        row = c.fetchone()
        conn.close()
        if row:
            import json
            return json.loads(row[0])
    
    # Fetch from API
    try:
        url = f"{POLYMARKET_API}/v1/leaderboard"
        params = {
            "category": category,
            "timePeriod": period,
            "limit": limit,
            "orderBy": "PNL"
        }
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            
            # Cache the result
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            import json
            c.execute("""
                INSERT OR REPLACE INTO trader_cache (category, period, data, updated_at)
                VALUES (?, ?, ?, datetime('now'))
            """, (category, period, json.dumps(data)))
            conn.commit()
            conn.close()
            
            return data
        return []
    except Exception as e:
        print(f"API error: {e}")
        return []

# Auth dependency
async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, telegram_id, username, tier FROM users WHERE api_token = ?", (token,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"id": row[0], "telegram_id": row[1], "username": row[2], "tier": row[3]}

# API Routes
@app.get("/")
def root():
    return {"message": "PolyStart API", "version": "1.0.0"}

@app.get("/traders")
def get_top_traders(
    category: str = "OVERALL", 
    period: str = "MONTH",
    limit: int = 20
):
    """Get top traders from Polymarket leaderboard"""
    if not check_rate_limit(None):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    traders = get_leaderboard(category, period, min(limit, 50))
    
    return [
        {
            "rank": t.get("rank", ""),
            "address": t.get("proxyWallet", ""),
            "username": t.get("userName", "Anonymous"),
            "pnl": round(t.get("pnl", 0), 2),
            "vol": round(t.get("vol", 0), 2),
            "verified": t.get("verifiedBadge", False)
        }
        for t in traders[:limit]
    ]

@app.get("/traders/{category}")
def get_category_traders(category: str, period: str = "MONTH", limit: int = 20):
    """Get top traders by category"""
    valid_categories = ["OVERALL", "POLITICS", "SPORTS", "CRYPTO", "CULTURE", "WEATHER", "ECONOMICS", "TECH", "FINANCE"]
    if category.upper() not in valid_categories:
        raise HTTPException(status_code=400, detail=f"Invalid category")
    
    if not check_rate_limit(None):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    traders = get_leaderboard(category.upper(), period, min(limit, 50))
    
    return [
        {
            "rank": t.get("rank", ""),
            "address": t.get("proxyWallet", ""),
            "username": t.get("userName", "Anonymous"),
            "pnl": round(t.get("pnl", 0), 2),
            "vol": round(t.get("vol", 0), 2),
            "verified": t.get("verifiedBadge", False)
        }
        for t in traders[:limit]
    ]

@app.post("/users")
def create_user(user: UserCreate):
    """Create new user with auto-generated API token"""
    token = secrets.token_urlsafe(32)
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO users (telegram_id, username, api_token, tier) 
            VALUES (?, ?, ?, 'free')
        """, (user.telegram_id, user.username, token))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        
        return {
            "user_id": user_id,
            "api_token": token,
            "tier": "free",
            "message": "User created successfully"
        }
    except sqlite3.IntegrityError:
        conn.close()
        # User exists, return existing token
        c = conn.cursor()
        c.execute("SELECT id, api_token, tier FROM users WHERE telegram_id = ?", (user.telegram_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return {"user_id": row[0], "api_token": row[1], "tier": row[2], "message": "User already exists"}
        raise HTTPException(status_code=400, detail="User already exists")

@app.get("/me")
def get_me(user = Depends(get_current_user)):
    """Get current user info"""
    return user

@app.post("/follow")
def follow_trader(req: FollowRequest, user = Depends(get_current_user)):
    """Follow a trader"""
    # Check tier limits
    if user["tier"] == "free":
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM followed_traders WHERE user_id = ?", (user["id"],))
        count = c.fetchone()[0]
        conn.close()
        
        if count >= 3:
            raise HTTPException(
                status_code=403, 
                detail="Free tier limit: max 3 follows. Upgrade to Pro for unlimited."
            )
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO followed_traders (user_id, trader_address, trader_name)
            VALUES (?, ?, ?)
        """, (user["id"], req.trader_address, req.trader_name))
        conn.commit()
        conn.close()
        return {"message": f"Now following {req.trader_name}"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Already following this trader")

@app.delete("/follow/{trader_address}")
def unfollow_trader(trader_address: str, user = Depends(get_current_user)):
    """Unfollow a trader"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM followed_traders WHERE user_id = ? AND trader_address = ?",
              (user["id"], trader_address))
    conn.commit()
    conn.close()
    return {"message": "Unfollowed successfully"}

@app.get("/follows")
def get_follows(user = Depends(get_current_user)):
    """Get user's followed traders"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT ft.trader_address, ft.trader_name, ft.added_at
        FROM followed_traders ft
        WHERE ft.user_id = ?
    """, (user["id"],))
    results = c.fetchall()
    conn.close()
    
    return [
        {"address": r[0], "name": r[1], "added_at": r[2]}
        for r in results
    ]

@app.get("/health")
def health_check():
    """Health check"""
    traders = get_leaderboard("OVERALL", "MONTH", 1, use_cache=False)
    api_status = "connected" if traders else "disconnected"
    
    # Count users
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    user_count = c.fetchone()[0]
    conn.close()
    
    return {
        "status": "healthy",
        "api": api_status,
        "users": user_count,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)