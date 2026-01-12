// API Configuration
// This file can be customized for different deployment environments
// For Vercel: Set environment variables API_BASE_URL and WS_BASE_URL in Vercel dashboard
// For GitHub Pages: Edit the default values below or use build-config.js

(function() {
  // Default values - will be replaced by build script if environment variables are set
  // For Vercel: Set API_BASE_URL and WS_BASE_URL in environment variables
  const API_BASE_URL = 'http://4.232.170.195/';
  const WS_BASE_URL = 'ws://4.232.170.195/';

  // Auto-detect protocol based on current page protocol
  const currentProtocol = window.location.protocol;
  const isSecure = currentProtocol === 'https:';
  
  let apiBase = API_BASE_URL;
  let wsBase = WS_BASE_URL;
  
  // IMPORTANT: Browsers block HTTP requests from HTTPS pages (mixed content)
  // If your API server supports HTTPS, use https:// URLs in environment variables
  // If your API server only supports HTTP, you have two options:
  // 1. Use a proxy/CORS proxy service
  // 2. Set up HTTPS on your API server
  
  // For now, keep the original protocol to avoid auto-conversion issues
  // If deployed on HTTPS and API is HTTP, browser will block it (this is expected)
  // You'll need to either:
  // - Set environment variables with https:// URLs if your API supports HTTPS
  // - Or use a CORS proxy
  if (isSecure && apiBase.startsWith('http://') && !apiBase.includes('4.232.170.195')) {
    // Only auto-convert for non-default APIs that might support HTTPS
    apiBase = apiBase.replace('http://', 'https://');
  }
  if (isSecure && wsBase.startsWith('ws://') && !wsBase.includes('4.232.170.195')) {
    wsBase = wsBase.replace('ws://', 'wss://');
  }
  
  // Log warning if there's a protocol mismatch
  if (isSecure && (apiBase.startsWith('http://') || wsBase.startsWith('ws://'))) {
    console.warn('⚠️ WARNING: HTTPS page trying to access HTTP API. Browser may block this due to mixed content policy.');
    console.warn('⚠️ Solution: Use HTTPS/WSS URLs or set up a CORS proxy.');
  }
  
  // Make available globally
  window.API_BASE_URL = apiBase;
  window.WS_BASE_URL = wsBase;
  
  console.log('API Configuration loaded:', {
    apiBase: apiBase,
    wsBase: wsBase,
    protocol: currentProtocol
  });
})();
