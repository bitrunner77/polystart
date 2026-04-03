# PolyStart 🏆

Beginner-friendly Polymarket copy trading tool.

## Features

- **Real-time Leaderboard** - Top traders by category (Politics, Sports, Crypto, etc.)
- **User Accounts** - Sign up and track your follows
- **Follow Traders** - Save your favorite traders to watch
- **Tier System** - Free (3 follows) vs Pro (unlimited)
- **Analytics** - Period comparison, category insights
- **Rate Limiting** - 100 req/hr free, cached responses
- **Telegram Alerts** - Get notified when traders make moves (coming soon)

## Tech Stack

- **Backend:** FastAPI + SQLite
- **Frontend:** React + Vite
- **Data:** Polymarket API
- **Hosting:** Render (backend) + Vercel (frontend)

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend
cd frontend
npm install
npm run dev
```

## API

| Endpoint | Description |
|----------|-------------|
| `GET /traders` | Top 20 traders |
| `GET /traders/{category}` | By category |
| `POST /users` | Create account |
| `POST /follow` | Follow trader |
| `GET /follows` | Your follows |
| `GET /analytics/trader/{addr}` | Trader insights |
| `GET /analytics/categories` | Category comparison |

## Deployment

See [DEPLOY.md](DEPLOY.md) for step-by-step deploy to Render + Vercel.

## Pricing

| Tier | Price | Features |
|------|-------|----------|
| Free | $0 | 3 follows, basic alerts |
| Pro | $9.99/mo | Unlimited follows, auto-copy, premium alerts |

## License

MIT