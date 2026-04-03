# 🚀 PolyStart Deployment Steps

## Option 1: Quick Deploy (GitHub + Auto-Deploy)

### Backend → Render (Free)
1. Go to https://dashboard.render.com
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub: `bitrunner77/polystart`
4. Select the **backend** folder
5. Configure:
   - Name: `polystart-backend`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Click **Deploy**
7. Wait 2-3 min → Copy your URL (e.g., `https://polystart-backend.onrender.com`)

### Frontend → Vercel (Free)
1. Go to https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. Import: `bitrunner77/polystart`
4. Select **frontend** folder
5. Framework: `Vite`
6. Add Environment Variable:
   - Key: `VITE_API_URL`
   - Value: `YOUR_RENDER_URL` (e.g., `https://polystart-backend.onrender.com`)
7. Click **Deploy**
8. Wait 1-2 min → Get your frontend URL

---

## Option 2: One-Click Deploy

Use this Render button (if configured):
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/bitrunner77/polystart)

---

## After Deploy - Test It

```bash
# Test health endpoint
curl https://YOUR_BACKEND_URL/health

# Test traders
curl https://YOUR_BACKEND_URL/traders
```

Expected response:
```json
{"status": "healthy", "api": "connected", ...}
```

---

## Troubleshooting

### CORS Errors
- Update `main.py` CORS to include your Vercel domain:
```python
allow_origins=["http://localhost:5173", "https://YOUR_APP.vercel.app"],
```

### 500 Error on Start
- Check Render logs in dashboard
- Make sure `sqlite3` path is writable (Render has ephemeral filesystem)

### API Not Working
- Wait 30s for cold start
- Check `/health` endpoint first

---

## Get Help

- Render docs: https://render.com/docs
- Vercel docs: https://vercel.com/docs