# Deploy to GitHub Pages - Complete Solution

## The Problem
GitHub Pages serves over HTTPS, but your API is HTTP. Browsers block this (mixed content).

## The Solution
Use a Vercel serverless function as a proxy that:
- Accepts HTTPS requests ✅
- Forwards to your HTTP API ✅
- Returns responses ✅

## Quick Setup (3 Steps)

### 1. Deploy Proxy to Vercel

**Option A: Using Vercel Dashboard**
1. Go to [vercel.com](https://vercel.com) → "Add New Project"
2. Create a new project
3. Upload just the `api/` folder
4. Deploy
5. Copy your proxy URL (e.g., `https://your-proxy.vercel.app/api/proxy`)

**Option B: Using Vercel CLI**
```bash
# Create a new directory
mkdir api-proxy && cd api-proxy

# Copy proxy file
cp ../api/proxy.js ./api/proxy.js

# Deploy
vercel
```

### 2. Update index.html

Uncomment line 13 in `index.html` and set your proxy URL:

```html
<script>window.API_PROXY_URL = "https://your-proxy.vercel.app/api/proxy";</script>
```

### 3. Deploy to GitHub Pages

1. Push to GitHub
2. Settings → Pages → Enable GitHub Pages
3. Done! 🎉

## How It Works

1. Your GitHub Pages site (HTTPS) makes request to proxy (HTTPS) ✅
2. Proxy forwards to your API (HTTP) ✅  
3. Proxy returns response to your site ✅

## Files You Need

- ✅ `api/proxy.js` - The proxy function (already created)
- ✅ `index.html` - Your frontend (update with proxy URL)
- ✅ `config.js` - Auto-detects and uses proxy

## Testing

1. Deploy proxy → Get URL
2. Update `index.html` with proxy URL
3. Deploy to GitHub Pages
4. Open site → Check browser console
5. Should see: `API Configuration loaded: { apiBase: "https://your-proxy..." }`

## Troubleshooting

**Still getting mixed content error?**
- Make sure proxy URL starts with `https://`
- Check that `window.API_PROXY_URL` is set BEFORE `config.js` loads
- Look at browser console for actual URLs being used

**Proxy not working?**
- Check Vercel function logs
- Test proxy directly: `curl "https://your-proxy.vercel.app/api/proxy?path=api/v1/nlp/index/info/test"`
- Verify your API server is accessible from Vercel

**File upload fails?**
- Proxy handles FormData automatically
- Check Vercel logs for errors
- Verify API endpoint accepts file uploads

## Alternative: Enable HTTPS on API Server

If you can enable HTTPS on `4.232.170.195`:
1. Get SSL certificate (Let's Encrypt is free)
2. Configure HTTPS
3. Update `config.js`: `const API_BASE_URL = 'https://4.232.170.195/';`
4. No proxy needed!
