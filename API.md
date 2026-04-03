# PolyStart - Complete Feature Summary

## API Endpoints

### Core
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| GET | `/traders` | Top 20 traders (overall) |
| GET | `/traders/{category}` | By category |
| POST | `/users` | Create account |
| GET | `/me` | Current user |
| POST | `/follow` | Follow trader |
| DELETE | `/follow/{addr}` | Unfollow |
| GET | `/follows` | My follows |

### Search & Discovery
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/search/trader?q=...` | Search traders |
| GET | `/search/markets?q=...` | Search markets |
| GET | `/trending` | Most active traders |
| GET | `/watchlist/recommendations` | Suggested traders |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/trader/{addr}` | Trader period analysis |
| GET | `/analytics/market` | Market stats |
| GET | `/analytics/categories` | Category comparison |

### Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/notifications/settings` | Get settings |
| POST | `/notifications/settings` | Update settings |
| POST | `/notifications/test` | Send test alert |

## Database Schema

### users
- id, telegram_id, username, api_token, tier, created_at

### followed_traders
- id, user_id, trader_address, trader_name, added_at

### trader_cache
- id, category, period, data, updated_at

### notification_settings
- user_id, telegram_enabled, webhook_enabled, webhook_url, email, etc.

## Tier Features

| Feature | Free | Pro |
|---------|------|-----|
| Follows | 3 | Unlimited |
| API calls/hr | 100 | Unlimited |
| Alerts | Daily | Real-time |
| Analytics | Basic | Advanced |
| Price | $0 | $9.99/mo |