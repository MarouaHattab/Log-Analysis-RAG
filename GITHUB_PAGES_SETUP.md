# Deploying to GitHub Pages - Complete Guide

## The Problem

GitHub Pages serves your site over **HTTPS**, but your API is **HTTP** (`http://4.232.170.195/`). Browsers block HTTP requests from HTTPS pages (mixed content policy).

## Solution: Use a Proxy

You need a proxy server that:
- Accepts HTTPS requests (from GitHub Pages)
- Forwards them to your HTTP API
- Returns the response

## Option 1: Deploy Proxy to Vercel (Recommended - Free & Easy)

### Step 1: Deploy Proxy to Vercel

1. Create a **new Vercel project** (separate from your frontend)
2. Upload just the `api/` folder from this repo
3. Or create a minimal repo with just:
   - `api/proxy.js` (the proxy function)
   - `vercel.json` (Vercel config)

**Quick Deploy:**
```bash
# Create a new directory
mkdir api-proxy
cd api-proxy

# Copy the proxy file
cp ../api/proxy.js ./api/proxy.js

# Create vercel.json
cat > vercel.json << EOF
{
  "version": 2,
  "builds": [
    {
      "src": "api/proxy.js",
      "use": "@vercel/node"
    }
  ],
  "routes": [
    {
      "src": "/api/proxy",
      "dest": "/api/proxy.js"
    }
  ]
}
EOF

# Deploy to Vercel
vercel
```

### Step 2: Get Your Proxy URL

After deploying, Vercel will give you a URL like:
```
https://your-proxy-name.vercel.app/api/proxy
```

### Step 3: Update Your HTML

In `index.html`, uncomment and update the proxy line:

```html
<script>window.API_PROXY_URL = "https://your-proxy-name.vercel.app/api/proxy";</script>
```

### Step 4: Deploy to GitHub Pages

1. Push your updated `index.html` to GitHub
2. Enable GitHub Pages in repository settings
3. Your site will now use the proxy!

## Option 2: Use a Free CORS Proxy Service

**Note:** These services are unreliable and not recommended for production.

1. Use a service like `https://cors-anywhere.herokuapp.com/`
2. Update `index.html`:
```html
<script>window.API_PROXY_URL = "https://cors-anywhere.herokuapp.com/http://4.232.170.195";</script>
```

**Warning:** These services often go down and have rate limits.

## Option 3: Enable HTTPS on Your API Server (Best Long-term Solution)

If you can enable HTTPS on `4.232.170.195`:

1. Get an SSL certificate (Let's Encrypt is free)
2. Configure your API server to serve HTTPS
3. Update `config.js`:
```javascript
const API_BASE_URL = 'https://4.232.170.195/';
const WS_BASE_URL = 'wss://4.232.170.195/';
```

## How the Proxy Works

The proxy (`api/proxy.js`) receives requests like:
```
GET https://your-proxy.vercel.app/api/proxy?path=api/v1/data/upload/test123
```

And forwards them to:
```
POST http://4.232.170.195/api/v1/data/upload/test123
```

## Testing the Proxy

1. Deploy proxy to Vercel
2. Test it directly:
```bash
curl "https://your-proxy.vercel.app/api/proxy?path=api/v1/nlp/index/info/test"
```

3. If it works, update your HTML with the proxy URL
4. Deploy to GitHub Pages

## Troubleshooting

### Proxy returns 500 error
- Check Vercel function logs
- Verify your API server is accessible from Vercel's servers
- Check that the path parameter is being passed correctly

### Still getting mixed content errors
- Make sure you set `window.API_PROXY_URL` BEFORE `config.js` loads
- Check browser console for the actual URL being used
- Verify proxy URL starts with `https://`

### WebSocket not working
- WebSocket proxying is more complex
- Consider enabling HTTPS on your API server for WebSocket support
- Or use polling instead of WebSocket for progress updates

## Quick Start Checklist

- [ ] Deploy `api/proxy.js` to Vercel
- [ ] Get your proxy URL (e.g., `https://xxx.vercel.app/api/proxy`)
- [ ] Update `index.html` with proxy URL
- [ ] Push to GitHub
- [ ] Enable GitHub Pages
- [ ] Test your deployed site!
