"""
PolyStart - Notifications System
Email, webhook, and Telegram alerts
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import sqlite3

router = APIRouter()

DB_FILE = 'polystart.db'

# Models
class NotificationSettings(BaseModel):
    telegram_enabled: bool = False
    webhook_enabled: bool = False
    webhook_url: str = ""
    email_enabled: bool = False
    email: str = ""
    alerts_new_trades: bool = True
    alerts_large_moves: bool = True
    alerts_daily_summary: bool = True

class TestAlertRequest(BaseModel):
    alert_type: str  # telegram, webhook, email

# Notification functions
def send_telegram_message(chat_id: str, message: str, token: str = None):
    """Send Telegram message"""
    if not token:
        return False, "No Telegram token configured"
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
        resp = requests.post(url, json=data, timeout=10)
        return resp.status_code == 200, "Sent" if resp.status_code == 200 else "Failed"
    except Exception as e:
        return False, str(e)

def send_webhook(url: str, payload: dict):
    """Send webhook notification"""
    if not url:
        return False, "No webhook URL"
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.status_code in [200, 201], "Sent" if resp.status_code in [200, 201] else "Failed"
    except Exception as e:
        return False, str(e)

def send_email(to: str, subject: str, body: str, smtp_config: dict = None):
    """Send email (requires SMTP config in production)"""
    # In production: implement with SendGrid, AWS SES, etc.
    return False, "Email not configured (use SendGrid/SES in production)"

# API Routes
@router.get("/notifications/settings")
def get_notification_settings(user_id: int):
    """Get user's notification settings"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT telegram_enabled, webhook_enabled, webhook_url, 
               email_enabled, email, alerts_new_trades, alerts_large_moves, alerts_daily_summary
        FROM notification_settings WHERE user_id = ?
    """, (user_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        # Return defaults
        return {
            "telegram_enabled": False,
            "webhook_enabled": False,
            "webhook_url": "",
            "email_enabled": False,
            "email": "",
            "alerts_new_trades": True,
            "alerts_large_moves": True,
            "alerts_daily_summary": True
        }
    
    return {
        "telegram_enabled": bool(row[0]),
        "webhook_enabled": bool(row[1]),
        "webhook_url": row[2] or "",
        "email_enabled": bool(row[3]),
        "email": row[4] or "",
        "alerts_new_trades": bool(row[5]),
        "alerts_large_moves": bool(row[6]),
        "alerts_daily_summary": bool(row[7])
    }

@router.post("/notifications/settings")
def update_notification_settings(user_id: int, settings: NotificationSettings):
    """Update notification settings"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute("""
        INSERT OR REPLACE INTO notification_settings 
        (user_id, telegram_enabled, webhook_enabled, webhook_url, 
         email_enabled, email, alerts_new_trades, alerts_large_moves, alerts_daily_summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        int(settings.telegram_enabled),
        int(settings.webhook_enabled),
        settings.webhook_url,
        int(settings.email_enabled),
        settings.email,
        int(settings.alerts_new_trades),
        int(settings.alerts_large_moves),
        int(settings.alerts_daily_summary)
    ))
    conn.commit()
    conn.close()
    
    return {"message": "Settings updated"}

@router.post("/notifications/test")
def test_alert(user_id: int, test: TestAlertRequest):
    """Send a test alert"""
    # Get user settings
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT telegram_id, webhook_url FROM users u
        LEFT JOIN notification_settings ns ON u.id = ns.user_id
        WHERE u.id = ?
    """, (user_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    
    telegram_id, webhook_url = row[0], row[1]
    
    if test.alert_type == "telegram":
        if not telegram_id:
            return {"success": False, "message": "No Telegram ID linked"}
        
        # Get token from env (would be stored securely in production)
        token = None  # os.environ.get("TELEGRAM_BOT_TOKEN")
        success, msg = send_telegram_message(telegram_id, "🧪 Test alert from PolyStart!", token)
        return {"success": success, "message": msg}
    
    elif test.alert_type == "webhook":
        if not webhook_url:
            return {"success": False, "message": "No webhook URL configured"}
        
        success, msg = send_webhook(webhook_url, {
            "event": "test",
            "message": "Test alert from PolyStart"
        })
        return {"success": success, "message": msg}
    
    return {"success": False, "message": "Unknown alert type"}

# Create notification settings table if not exists
def init_notifications():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notification_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        telegram_enabled INTEGER DEFAULT 0,
        webhook_enabled INTEGER DEFAULT 0,
        webhook_url TEXT,
        email_enabled INTEGER DEFAULT 0,
        email TEXT,
        alerts_new_trades INTEGER DEFAULT 1,
        alerts_large_moves INTEGER DEFAULT 1,
        alerts_daily_summary INTEGER DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    conn.commit()
    conn.close()

init_notifications()