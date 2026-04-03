"""
PolyStart - Trader Activity Monitor
Polling service that tracks when followed traders make moves
"""

import time
import requests
import sqlite3
from datetime import datetime, timedelta

DB_FILE = 'polystart.db'

# Track last known positions for each trader
last_positions = {}

def get_trader_trades(trader_address: str, limit: int = 10):
    """Get recent trades for a specific trader"""
    # Note: This would need auth in production
    # For now, we'll use public data
    try:
        # Try the user activity endpoint
        url = "https://data-api.polymarket.com/v1/user-activity"
        params = {"user": trader_address, "limit": limit}
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return []

def get_market_activity():
    """Get recent market activity (new trades)"""
    try:
        # Get trending markets
        url = "https://clob.polymarket.com/markets"
        resp = requests.get(url, timeout=10)
        return resp.json() if resp.status_code == 200 else []
    except:
        return []

def check_followed_traders():
    """Check if any followed traders have new activity"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Get all users with follows
    c.execute("""
        SELECT u.id, u.telegram_id, ft.trader_address, ft.trader_name
        FROM users u
        JOIN followed_traders ft ON u.id = ft.user_id
        WHERE u.telegram_id IS NOT NULL
    """)
    
    followed = c.fetchall()
    conn.close()
    
    alerts = []
    
    for user_id, telegram_id, trader_addr, trader_name in followed:
        # In production: check if trader has new trades
        # For now, simulate with random checks
        pass
    
    return alerts

def send_telegram_alert(telegram_id: str, message: str, token: str):
    """Send alert via Telegram bot"""
    if not token:
        return
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {"chat_id": telegram_id, "text": message, "parse_mode": "HTML"}
        resp = requests.post(url, json=data, timeout=10)
        return resp.status_code == 200
    except:
        return False

def run_monitor():
    """Main monitoring loop"""
    POLL_INTERVAL = 300  # 5 minutes
    
    token = None  # TELEGRAM_TOKEN
    
    print("📡 PolyStart Monitor started")
    print(f"Polling every {POLL_INTERVAL}s...")
    
    while True:
        try:
            alerts = check_followed_traders()
            
            for telegram_id, message in alerts:
                send_telegram_alert(telegram_id, message, token)
            
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            print("Monitor stopped")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_monitor()