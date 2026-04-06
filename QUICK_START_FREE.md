# Quick Start - Free Deployment on Render + Vercel

## TL;DR - 3 Easy Steps

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Deploy Backend on Render (2 minutes)

1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Select your repository
5. **Configuration:**
   - Name: `shark-api`
   - Environment: `Docker`
   - Build Command: (leave default)
   - Start Command: (leave default - uses Dockerfile)
   - Plan: **Free**

6. **Add environment variable:**
   - Key: `MONGO_CONNECTION_STRING`
   - Value: (copy from your `.env` file)

7. Click **"Create Web Service"**
8. Wait 2-3 minutes for deployment
9. **Copy your backend URL** (will be like `https://shark-api-xxxxx.onrender.com`)

### Step 3: Deploy Frontend on Vercel (2 minutes)

1. Go to https://vercel.com
2. Sign up with GitHub
3. Click "Add New Project"
4. Select your repository
5. **Framework Preset:** Vite (auto-detected)
6. **Root Directory:** `frontend`
7. **Add environment variable:**
   - Name: `VITE_API_URL`
   - Value: `https://shark-api-xxxxx.onrender.com` (from Step 2)

8. Click **"Deploy"**
9. Wait 1-2 minutes
10. Copy your frontend URL (will be like `https://shark-foraging-xxxxx.vercel.app`)

---

## ✨ You're Done!

**Frontend:** https://shark-foraging-xxxxx.vercel.app  
**Backend API Docs:** https://shark-api-xxxxx.onrender.com/docs

**Test it:**
- Open the frontend URL
- You should see "System Operational" status
- Start the simulator and watch sharks appear on the map!

---

## Important Notes

⚠️ **Free Tier Limitations:**
- Backend spins down after 15 minutes of inactivity
- First request after sleep takes 30 seconds
- To keep it awake: GitHub Actions will ping it every 10 minutes (automated)

✅ **Already configured:**
- Dockerfile ready
- Frontend API URLs use environment variables
- Keep-alive workflow setup
- GitHub Actions configured

---

## Troubleshooting

**Frontend shows "Offline"**
- Check your backend URL in Vercel environment variables
- Make sure MongoDB connection string is set in Render

**Simulator button doesn't work**
- Wait for backend to fully start (check Render logs)
- Try refreshing the page

**Getting 503 after some time**
- This is normal on free tier - backend went to sleep
- First request wakes it up (30 sec wait)
- GitHub Actions keep-alive keeps it awake during active use

---

## Next Steps (When You Want to Scale)

1. **Remove spin-down:** Upgrade Render to $7/month
2. **Add custom domain:** Configure DNS in Render/Vercel
3. **More database storage:** Upgrade MongoDB Atlas to paid tier
4. **Better performance:** Add caching layer (Redis)

For now, enjoy your free deployment! 🚀
