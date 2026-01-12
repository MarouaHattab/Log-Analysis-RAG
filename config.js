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
  
  // Determine if we need to use a proxy
  const needsProxy = isSecure && API_BASE_URL.startsWith('http://');
  const useProxy = PROXY_URL && needsProxy;
  
  let apiBase = API_BASE_URL;
  
  if (useProxy) {
    // When using proxy, apiBase becomes the proxy URL
    // Remove trailing slash - we'll add ?path= parameter
    apiBase = PROXY_URL.endsWith('/') ? PROXY_URL.slice(0, -1) : PROXY_URL;
  } else if (needsProxy && !PROXY_URL) {
    // Need proxy but not provided
    console.error('❌ Mixed Content Error: HTTPS page cannot access HTTP API.');
    console.error('💡 Solution: Set window.API_PROXY_URL before config.js loads.');
    console.error('💡 Example: <script>window.API_PROXY_URL = "https://your-proxy.vercel.app/api/proxy";</script>');
  }
  
  // Override apiBase to use helper function when proxy is active
  // Create a helper function to build API URLs
  window.buildApiUrl = function(path) {
    if (useProxy) {
      // Remove leading slash from path if present
      const cleanPath = path.startsWith('/') ? path.slice(1) : path;
      return `${apiBase}?path=${encodeURIComponent(cleanPath)}`;
    } else {
      // Normal URL construction
      const base = apiBase.endsWith('/') ? apiBase : apiBase + '/';
      const cleanPath = path.startsWith('/') ? path.slice(1) : path;
      return base + cleanPath;
    }
  };
  
  // Store original apiBase for reference
  const originalApiBase = apiBase;
  
  // Override apiBase getter to use buildApiUrl when proxy is active
  // But keep it simple - just modify how URLs are constructed in fetch calls
  Object.defineProperty(window, 'API_BASE_URL', {
    get: function() {
      return originalApiBase;
    },
    configurable: true
  });
  
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
