// API Configuration
// This file can be customized for different deployment environments
// For Vercel: Set environment variables API_BASE_URL and WS_BASE_URL in Vercel dashboard
// For GitHub Pages: Edit the default values below or use build-config.js

(function() {
  // Default values - will be replaced by build script if environment variables are set
  // For Vercel/GitHub Pages: Set API_BASE_URL and WS_BASE_URL via env or edit below
  // NOTE: If hosting the frontend on HTTPS (GitHub Pages), the API must be reachable via HTTPS
  //       Use a HTTPS proxy if your API is HTTP-only. Set window.API_PROXY_URL to your proxy.
  const API_BASE_URL = 'http://4.232.170.195/';
  const WS_BASE_URL = 'ws://4.232.170.195/';
  const PROXY_URL = window.API_PROXY_URL || '';

  // Auto-detect protocol based on current page protocol
  const currentProtocol = window.location.protocol;
  const isSecure = currentProtocol === 'https:';
  
  // If a proxy is provided, route HTTP calls through the proxy (must be HTTPS-compatible)
  // PROXY_URL example: 'https://your-proxy.example.com/' that forwards to the API
  const apiBase = PROXY_URL
    ? (PROXY_URL.endsWith('/') ? PROXY_URL : PROXY_URL + '/')
    : API_BASE_URL;
  
  // WebSocket base stays as-is (proxying WS via static hosting is non-trivial)
  let wsBase = WS_BASE_URL;
  
  // If page is HTTPS and wsBase is ws://, browsers may block it; warn the user
  if (isSecure && wsBase.startsWith('ws://')) {
    console.warn('⚠️ WARNING: HTTPS page trying to connect to ws:// WebSocket. This may be blocked. Prefer wss://.');
  }
  
  // Make available globally
  window.API_BASE_URL = apiBase;
  window.WS_BASE_URL = wsBase;
  window.API_PROXY_URL = PROXY_URL;
  
  console.log('API Configuration loaded:', {
    apiBase: apiBase,
    wsBase: wsBase,
    protocol: currentProtocol
  });
})();
