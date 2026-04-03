"""
PolyStart Telegram Bot
Sends alerts when followed traders make moves
"""

import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Bot configuration
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")

# In-memory user storage (use database in production)
user_watchlists = {}  # {user_id: [trader_addresses]}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "👋 Welcome to PolyStart!\n\n"
        "The easiest way to follow top Polymarket traders.\n\n"
        "Commands:\n"
        "/traders - See top traders\n"
        "/follow <address> - Follow a trader\n"
        "/myfollows - Your watchlist\n"
        "/help - Get help\n\n"
        "Start by checking out top traders with /traders"
    )

async def traders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show top traders"""
    try:
        resp = requests.get(
            "https://data-api.polymarket.com/v1/leaderboard",
            params={"category": "OVERALL", "timePeriod": "MONTH", "limit": 10},
            timeout=10
        )
        traders = resp.json()
        
        msg = "🏆 Top 10 Traders This Month:\n\n"
        for t in traders:
            pnl = round(t.get("pnl", 0), 2)
            vol = round(t.get("vol", 0), 2)
            verified = "✅" if t.get("verifiedBadge") else ""
            msg += f"#{t.get('rank')} {t.get('userName', 'Anonymous')[:15]} {verified}\n"
            msg += f"   PnL: ${pnl:,.2f} | Vol: ${vol:,.0f}\n\n"
        
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"Error fetching traders: {e}")

async def follow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Follow a trader"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("Usage: /follow <trader_address>\n\nExample: /follow 0x492442eab586f242b53bda933fd5de859c8a3782")
        return
    
    address = context.args[0].lower()
    
    if user_id not in user_watchlists:
        user_watchlists[user_id] = []
    
    if address not in user_watchlists[user_id]:
        user_watchlists[user_id].append(address)
        await update.message.reply_text(f"✅ Now following: {address[:10]}...")
    else:
        await update.message.reply_text("You're already following this trader")

async def myfollows_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's followed traders"""
    user_id = update.effective_user.id
    
    if user_id not in user_watchlists or not user_watchlists[user_id]:
        await update.message.reply_text("You haven't followed any traders yet.\nUse /traders to find traders to follow.")
        return
    
    msg = "👀 Your Watchlist:\n\n"
    for addr in user_watchlists[user_id]:
        msg += f"• {addr[:10]}...\n"
    
    await update.message.reply_text(msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    await update.message.reply_text(
        "📖 PolyStart Help\n\n"
        "1. Use /traders to see top performers\n"
        "2. Copy a trader address\n"
        "3. Use /follow <address> to add to watchlist\n"
        "4. Use /myfollows to see your watchlist\n\n"
        "Coming soon: Real-time alerts when your traders make moves!"
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    print(f"Error: {context.error}")
    if update and update.message:
        await update.message.reply_text("Something went wrong. Please try again.")

def run_bot():
    """Run the Telegram bot"""
    if not TELEGRAM_TOKEN:
        print("⚠️ TELEGRAM_TOKEN not set. Bot won't run.")
        print("Set TELEGRAM_TOKEN env var to enable alerts.")
        return
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("traders", traders_command))
    app.add_handler(CommandHandler("follow", follow_command))
    app.add_handler(CommandHandler("myfollows", myfollows_command))
    app.add_handler(CommandHandler("help", help_command))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    print("🤖 PolyStart Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    run_bot()