"""
PolyStart - Analytics & Insights
Provide additional data about traders beyond just PNL
"""

from fastapi import APIRouter, Query
import requests

router = APIRouter()

POLYMARKET_API = "https://data-api.polymarket.com"

@router.get("/analytics/trader/{address}")
def get_trader_analytics(address: str):
    """Get detailed analytics for a specific trader"""
    
    # Fetch trader data from multiple periods
    periods = ["DAY", "WEEK", "MONTH", "ALL"]
    data = {}
    
    for period in periods:
        try:
            resp = requests.get(
                f"{POLYMARKET_API}/v1/leaderboard",
                params={"user": address, "timePeriod": period},
                timeout=10
            )
            if resp.status_code == 200:
                result = resp.json()
                if result:
                    data[period.lower()] = {
                        "pnl": result[0].get("pnl", 0),
                        "vol": result[0].get("vol", 0),
                        "rank": result[0].get("rank", "N/A")
                    }
        except:
            pass
    
    return {
        "address": address,
        "periods": data,
        "insights": generate_insights(data)
    }

def generate_insights(data: dict) -> dict:
    """Generate insights from trader data"""
    
    if not data:
        return {"message": "No data available"}
    
    # Compare periods
    day_pnl = data.get("day", {}).get("pnl", 0)
    week_pnl = data.get("week", {}).get("pnl", 0)
    month_pnl = data.get("month", {}).get("pnl", 0)
    
    # Trend analysis
    if day_pnl > week_pnl > 0:
        trend = "hot"
        message = "🔥 Trader is heating up this week!"
    elif day_pnl < 0 and week_pnl < 0:
        trend = "cold"
        message = "❄️ Trader is in a cold streak"
    elif week_pnl > month_pnl * 0.3:
        trend = "consistent"
        message = "📈 Strong consistent performer"
    else:
        trend = "volatile"
        message = "⚡ High volatility trader"
    
    return {
        "trend": trend,
        "message": message,
        "day_pnl": day_pnl,
        "week_pnl": week_pnl,
        "month_pnl": month_pnl
    }

@router.get("/analytics/market")
def get_market_analytics(category: str = "OVERALL"):
    """Get market-wide analytics"""
    
    # Get top traders
    try:
        resp = requests.get(
            f"{POLYMARKET_API}/v1/leaderboard",
            params={"category": category, "timePeriod": "WEEK", "limit": 50},
            timeout=10
        )
        
        if resp.status_code == 200:
            traders = resp.json()
            
            # Calculate aggregate stats
            total_pnl = sum(t.get("pnl", 0) for t in traders)
            total_vol = sum(t.get("vol", 0) for t in traders)
            profitable = sum(1 for t in traders if t.get("pnl", 0) > 0)
            
            return {
                "category": category,
                "top_traders": len(traders),
                "total_pnl": round(total_pnl, 2),
                "total_volume": round(total_vol, 2),
                "win_rate": f"{profitable / len(traders) * 100:.1f}%",
                "avg_pnl": round(total_pnl / len(traders), 2) if traders else 0
            }
    except Exception as e:
        return {"error": str(e)}
    
    return {"error": "Failed to fetch data"}

@router.get("/analytics/categories")
def get_category_comparison():
    """Compare performance across categories"""
    
    categories = ["POLITICS", "SPORTS", "CRYPTO", "CULTURE", "ECONOMICS", "TECH", "FINANCE"]
    results = []
    
    for cat in categories:
        try:
            resp = requests.get(
                f"{POLYMARKET_API}/v1/leaderboard",
                params={"category": cat, "timePeriod": "WEEK", "limit": 20},
                timeout=10
            )
            
            if resp.status_code == 200:
                traders = resp.json()
                total_pnl = sum(t.get("pnl", 0) for t in traders)
                total_vol = sum(t.get("vol", 0) for t in traders)
                
                results.append({
                    "category": cat,
                    "total_pnl": round(total_pnl, 2),
                    "total_volume": round(total_vol, 2),
                    "top_pnl": round(traders[0].get("pnl", 0), 2) if traders else 0
                })
        except:
            pass
    
    # Sort by total PNL
    results.sort(key=lambda x: x["total_pnl"], reverse=True)
    
    return {"categories": results}