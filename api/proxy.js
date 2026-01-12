/**
 * Vercel Serverless Function - API Proxy
 * This proxies requests from HTTPS (GitHub Pages/Vercel) to HTTP API
 * 
 * Deploy this to Vercel separately, then update config.js to use the proxy URL
 */

export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // Get the API path from query parameter
  // Frontend calls: https://proxy.vercel.app/api/proxy?path=api/v1/data/upload/test123
  const apiPath = req.query.path || '';
  const apiBase = 'http://4.232.170.195/';
  
  if (!apiPath) {
    return res.status(400).json({ error: 'Missing path parameter. Use ?path=api/v1/...' });
  }
  
  // Ensure path doesn't start with / and apiBase ends with /
  const cleanPath = apiPath.startsWith('/') ? apiPath.slice(1) : apiPath;
  const cleanBase = apiBase.endsWith('/') ? apiBase : apiBase + '/';
  const targetUrl = `${cleanBase}${cleanPath}`;

  try {
    // Prepare fetch options
    const fetchOptions = {
      method: req.method,
    };

    // Handle body for non-GET requests
    if (req.method !== 'GET' && req.body) {
      const contentType = req.headers['content-type'] || '';
      
      if (contentType.includes('multipart/form-data') || contentType.includes('form-data')) {
        // For FormData (file uploads)
        // Vercel parses FormData, so req.body might be an object
        // We need to reconstruct FormData for the fetch call
        const formData = new FormData();
        for (const [key, value] of Object.entries(req.body)) {
          if (value instanceof File || value instanceof Blob) {
            formData.append(key, value);
          } else {
            formData.append(key, String(value));
          }
        }
        fetchOptions.body = formData;
        // Don't set Content-Type - fetch will set it with boundary
      } else {
        // For JSON requests
        fetchOptions.headers = {
          'Content-Type': 'application/json',
        };
        // If body has a path, remove it before forwarding
        const { path, ...bodyWithoutPath } = req.body;
        fetchOptions.body = JSON.stringify(bodyWithoutPath);
      }
    }

    // Forward query parameters (except 'path')
    const queryParams = new URLSearchParams();
    Object.keys(req.query).forEach(key => {
      if (key !== 'path') {
        queryParams.append(key, req.query[key]);
      }
    });
    
    const finalUrl = queryParams.toString() 
      ? `${targetUrl}?${queryParams.toString()}`
      : targetUrl;

    console.log(`Proxying ${req.method} ${finalUrl}`);

    // Make request to actual API
    const response = await fetch(finalUrl, fetchOptions);
    
    // Get response data
    const contentType = response.headers.get('content-type');
    let data;
    
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    // Forward status and data
    res.status(response.status).json(data);
  } catch (error) {
    console.error('Proxy error:', error);
    res.status(500).json({ 
      error: 'Proxy error', 
      message: error.message,
      details: 'Failed to connect to API server'
    });
  }
}
