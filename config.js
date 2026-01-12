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
  // If page is served over HTTPS, use HTTPS/WSS for API
  const currentProtocol = window.location.protocol;
  const isSecure = currentProtocol === 'https:';
  
  // Convert HTTP to HTTPS and WS to WSS if page is served over HTTPS
  let apiBase = API_BASE_URL;
  let wsBase = WS_BASE_URL;
  
  if (isSecure) {
    // Replace http:// with https://
    if (apiBase.startsWith('http://')) {
      apiBase = apiBase.replace('http://', 'https://');
    }
    // Replace ws:// with wss://
    if (wsBase.startsWith('ws://')) {
      wsBase = wsBase.replace('ws://', 'wss://');
    }
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
