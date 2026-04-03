# PolyStart - MVP Plan

## Problem
Polymarket has 179+ tools but ALL are for advanced traders. Beginners struggle with:
- No simple "start here" guide
- Complex UI with no explanations
- Hard to find good traders to follow
- Overwhelming when first starting

## Solution
**PolyStart** - The beginner-friendly Polymarket companion

### Core Features (MVP)
1. **Curated Trader Lists** - Pre-vetted top traders by category (politics, sports, crypto)
2. **One-Tap Follow** - Add trader to watchlist in 1 click
3. **Simple Alerts** - Get notified when tracked traders make moves
4. **Beginner Guide** - "How to start trading" walkthrough
5. **Copy % Settings** - Automatically follow at % of their position size

### Pricing
- **Free:** Follow 3 traders, basic alerts
- **Pro ($9.99/mo):** Unlimited follows, auto-copy, advanced analytics

### Tech Stack
- **Backend:** FastAPI (Python) 
- **Frontend:** React (simple dashboard)
- **Hosting:** Render free tier → $10/mo
- **Database:** SQLite (free) → PostgreSQL later
- **API:** Polymarket GraphQL (free)
- **Notifications:** Telegram Bot API (free)

### 30-Day Roadmap

#### Week 1: Foundation
- [ ] Set up GitHub repo
- [ ] Design database schema (traders, users, alerts)
- [ ] Connect to Polymarket API (test data)
- [ ] Build simple API endpoint: get_top_traders()

#### Week 2: Core Features  
- [ ] Build Telegram bot for alerts
- [ ] Create React frontend (dashboard)
- [ ] Add "follow trader" functionality
- [ ] Test with 5 beta users

#### Week 3: Launch
- [ ] Deploy to Render
- [ ] Set up Stripe billing (for Pro)
- [ ] Launch on Reddit/Twitter
- [ ] Get first 10 users

#### Week 4: Iterate
- [ ] Gather feedback
- [ ] Fix top 3 issues
- [ ] First paying customer
- [ ] Plan Phase 2 (auto-copy, more features)

### Monthly Cost Estimate
| Item | Cost |
|------|------|
| Render (backend) | $0-10 |
| Domain | $12/yr |
| Stripe | Free |
| Polymarket API | Free |
| **Total** | **$10-15/mo** ✅

### Differentiation vs Competition
| Competitor | What they do | PolyStart |
|------------|--------------|-----------|
| PolyCop | Advanced copy trading | SIMPLE for beginners |
| PolyGun | All-in-one terminal | Focus on ONE thing (copy) |
| Polycool | Whale tracking | Curated + explained |
| okbet | Cross-platform | Just Polymarket (simpler) |

### Key Insight
All competitors are for people who ALREADY know how to trade. 
**PolyStart is for people who want to LEARN while copying.**