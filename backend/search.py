"""
PolyStart - Search & Discovery
Find specific traders or markets
"""

from fastapi import APIRouter, Query
import requests

router = APIRouter()

POLYMARKET_API = "https://data-api.polymarket.com"

@router.get("/search/trader")
def search_trader(q: str = Query(..., min_length=3)):
    """Search for a trader by address or username"""
    
    # Search in recent leaderboards
    results = []
    seen_addresses = set()
    
    for category in ["OVERALL", "POLITICS", "SPORTS", "CRYPTO"]:
        try:
            resp = requests.get(
                f"{POLYMARKET_API}/v1/leaderboard",
                params={"category": category, "timePeriod": "MONTH", "limit": 50},
                timeout=10
            )
            if resp.status_code == 200:
                traders = resp.json()
                for t in traders:
                    addr = t.get("proxyWallet", "")
                    if addr in seen_addresses:
                        continue
                    
                    username = t.get("userName", "").lower()
                    if q.lower() in username or q.lower() in addr:
                        results.append({
                            "address": addr,
                            "username": t.get("userName", "Anonymous"),
                            "category": category,
                            "pnl": round(t.get("pnl", 0), 2),
                            "vol": round(t.get("vol", 0), 2),
                            "rank": t.get("rank", "N/A")
                        })
                        seen_addresses.add(addr)
                        
        except:
            pass
    
    return {"results": results[:10], "query": q}

@router.get("/search/markets")
def search_markets(q: str = Query(..., min_length=2)):
    """Search for markets"""
    
    try:
        resp = requests.get(
            "https://clob.polymarket.com/markets",
            params={"search": q},
            timeout=10
        )
        
        if resp.status_code == 200:
            markets = resp.json()
            return {
                "results": [
                    {
                        "id": m.get("conditionId"),
                        "question": m.get("question"),
                        "volume": m.get("volume"),
                        "liquidity": m.get("liquidity")
                    }
                    for m in markets[:10]
                ],
                "query": q
            }
    except:
        pass
    
    return {"results": [], "query": q}

@router.get("/trending")
def get_trending(category: str = "OVERALL", period: str = "WEEK"):
    """Get trending traders with biggest recent moves"""
    
    try:
        resp = requests.get(
            f"{POLYMARKET_API}/v1/leaderboard",
            params={"category": category, "timePeriod": period, "limit": 50, "orderBy": "VOL"},
            timeout=10
        )
        
        if resp.status_code == 200:
            traders = resp.json()
            # Sort by volume (most active)
            traders.sort(key=lambda x: x.get("vol", 0), reverse=True)
            
            return {
                "category": category,
                "period": period,
                "trending": [
                    {
                        "rank": t.get("rank"),
                        "address": t.get("proxyWallet"),
                        "username": t.get("userName", "Anonymous"),
                        "pnl": round(t.get("pnl", 0), 2),
                        "volume": round(t.get("vol", 0), 2)
                    }
                    for t in traders[:20]
                ]
            }
    except Exception as e:
        return {"error": str(e)}
    
    return {"error": "Failed to fetch trending"}

@router.get("/watchlist/recommendations")
def get_recommendations():
    """Get recommended traders to follow"""
    
    recommendations = []
    seen = set()
    
    # Get top from each category
    categories = ["POLITICS", "SPORTS", "CRYPTO"]
    
    for cat in categories:
        try:
            resp = requests.get(
                f"{POLYMARKET_API}/v1/leaderboard",
                params={"category": cat, "timePeriod": "MONTH", "limit": 5},
                timeout=10
            )
            
            if resp.status_code == 200:
                traders = resp.json()
                for t in traders:
                    addr = t.get("proxyWallet", "")
                    if addr in seen:
                        continue
                    
                    recommendations.append({
                        "address": addr,
                        "username": t.get("userName", "Anonymous"),
                        "category": cat,
                        "reason": f"Top {cat.lower()} trader",
                        "pnl": round(t.get("pnl", 0), 2),
                        "vol": round(t.get("vol", 0), 2),
                        "verified": t.get("verifiedBadge", False)
                    })
                    seen.add(addr)
                    
        except:
            pass
    
    # Sort by PNL
    recommendations.sort(key=lambda x: x["pnl"], reverse=True)
    
    return {"recommendations": recommendations[:15]}