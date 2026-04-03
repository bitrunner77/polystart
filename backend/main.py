"""
PolyStart Backend - FastAPI + Real Polymarket API
Beginner-friendly Polymarket copy trading tool
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import requests
from datetime import datetime

app = FastAPI(title="PolyStart API")

# Database setup
def init_db():
    conn = sqlite3.connect('polystart.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id TEXT UNIQUE,
        username TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS followed_traders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        trader_address TEXT,
        category TEXT,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    conn.commit()
    conn.close()

init_db()

# Models
class UserCreate(BaseModel):
    telegram_id: str
    username: str

class FollowTrader(BaseModel):
    user_id: int
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

def get_leaderboard(category: str = "OVERALL", period: str = "MONTH", limit: int = 20) -> List[dict]:
    """Fetch top traders from Polymarket API"""
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
            return resp.json()
        return []
    except Exception as e:
        print(f"API error: {e}")
        return []

# API Routes
@app.get("/")
def root():
    return {"message": "PolyStart API - Beginner Polymarket Copy Trading"}

@app.get("/traders")
def get_top_traders(category: str = "OVERALL", period: str = "MONTH") -> List[TraderResponse]:
    """Get top traders from Polymarket leaderboard"""
    traders = get_leaderboard(category, period, 20)
    
    return [
        {
            "rank": t.get("rank", ""),
            "address": t.get("proxyWallet", ""),
            "username": t.get("userName", "Anonymous"),
            "pnl": round(t.get("pnl", 0), 2),
            "vol": round(t.get("vol", 0), 2),
            "verified": t.get("verifiedBadge", False)
        }
        for t in traders[:20]
    ]

@app.get("/traders/{category}")
def get_category_traders(category: str, period: str = "MONTH") -> List[TraderResponse]:
    """Get top traders by category (POLITICS, SPORTS, CRYPTO, etc.)"""
    valid_categories = ["OVERALL", "POLITICS", "SPORTS", "CRYPTO", "CULTURE", "WEATHER", "ECONOMICS", "TECH", "FINANCE"]
    if category.upper() not in valid_categories:
        raise HTTPException(status_code=400, detail=f"Invalid category. Use: {valid_categories}")
    
    traders = get_leaderboard(category.upper(), period, 20)
    
    return [
        {
            "rank": t.get("rank", ""),
            "address": t.get("proxyWallet", ""),
            "username": t.get("userName", "Anonymous"),
            "pnl": round(t.get("pnl", 0), 2),
            "vol": round(t.get("vol", 0), 2),
            "verified": t.get("verifiedBadge", False)
        }
        for t in traders[:20]
    ]

@app.post("/users")
def create_user(user: UserCreate):
    """Create new user"""
    conn = sqlite3.connect('polystart.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (telegram_id, username) VALUES (?, ?)",
                  (user.telegram_id, user.username))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return {"user_id": user_id, "message": "User created"}
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="User already exists")

@app.get("/users/{telegram_id}")
def get_user(telegram_id: str):
    """Get user by telegram ID"""
    conn = sqlite3.connect('polystart.db')
    c = conn.cursor()
    c.execute("SELECT id, telegram_id, username, created_at FROM users WHERE telegram_id = ?", (telegram_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"id": row[0], "telegram_id": row[1], "username": row[2], "created_at": row[3]}

@app.post("/follow")
def follow_trader(follow: FollowTrader):
    """Follow a trader"""
    conn = sqlite3.connect('polystart.db')
    c = conn.cursor()
    c.execute("INSERT INTO followed_traders (user_id, trader_address) VALUES (?, ?)",
              (follow.user_id, follow.trader_address))
    conn.commit()
    conn.close()
    return {"message": "Trader followed successfully"}

@app.get("/users/{user_id}/follows")
def get_user_follows(user_id: int):
    """Get user's followed traders"""
    conn = sqlite3.connect('polystart.db')
    c = conn.cursor()
    c.execute("SELECT trader_address, category, added_at FROM followed_traders WHERE user_id = ?", (user_id,))
    results = c.fetchall()
    conn.close()
    return [{"trader": r[0], "added_at": r[1]} for r in results]

@app.get("/health")
def health_check():
    """Health check"""
    # Test API connectivity
    traders = get_leaderboard("OVERALL", "MONTH", 1)
    api_status = "connected" if traders else "disconnected"
    
    return {
        "status": "healthy",
        "api": api_status,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)