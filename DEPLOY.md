# PolyStart - Deploy to Render

## Quick Deploy (5 minutes)

### 1. Create Render Account
- Go to [render.com](https://render.com)
- Sign up with GitHub

### 2. Deploy Backend
1. Click "New" → "Web Service"
2. Connect your GitHub repo: `bitrunner77/polystart`
3. Select the `backend` folder
4. Configure:
   - Name: `polystart-backend`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Click "Deploy"

### 3. Get API URL
After deploy, you'll get a URL like:
`https://polystart-backend.onrender.com`

### 4. Deploy Frontend
1. Go to [Vercel.com](https://vercel.com)
2. Import your GitHub repo
3. Select the `frontend` folder
4. Add environment variable:
   - `VITE_API_URL` = your Render backend URL
5. Deploy

## Manual Deploy (Alternative)

```bash
# Backend (local)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (local)
cd frontend
npm install
npm run dev
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Health check |
| `GET /traders` | Top 20 traders (overall) |
| `GET /traders/{category}` | Traders by category |
| `POST /users` | Create user |
| `POST /follow` | Follow a trader |
| `GET /health` | API status |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_TOKEN` | No | For Telegram bot alerts |

## Troubleshooting

### CORS errors
The backend already has CORS enabled for localhost:5173 and Vercel.

### API not responding
Check Render logs in the dashboard.

### Rate limiting
Polymarket API may limit requests. Add caching if needed.