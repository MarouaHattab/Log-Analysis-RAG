# Test script for Mini-RAG API
# Run this after the server is running

Write-Host "Testing Mini-RAG API Routes..." -ForegroundColor Cyan
Write-Host ""

# Test 1: Welcome endpoint
Write-Host "1. Testing /api/v1/ (Welcome)" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/" -Method GET -ErrorAction Stop
    Write-Host "   ✓ SUCCESS" -ForegroundColor Green
    Write-Host "   Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Gray
} catch {
    Write-Host "   ✗ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: Upload file endpoint (will fail without file, but should not give 404)
Write-Host "2. Testing /api/v1/data/upload/1 (File Upload)" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/data/upload/1" -Method POST -ErrorAction Stop
    Write-Host "   Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Gray
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "   ✗ FAILED: 404 Not Found (Route not registered)" -ForegroundColor Red
    } elseif ($_.Exception.Response.StatusCode -eq 422) {
        Write-Host "   ✓ Route exists (422 = validation error, expected without file)" -ForegroundColor Green
    } else {
        Write-Host "   Response: $($_.Exception.Response.StatusCode)" -ForegroundColor Gray
    }
}
Write-Host ""

# Test 3: Get vector DB info
Write-Host "3. Testing /api/v1/nlp/index/info/1 (Vector DB Info)" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/nlp/index/info/1" -Method GET -ErrorAction Stop
    Write-Host "   ✓ SUCCESS" -ForegroundColor Green
    Write-Host "   Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Gray
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "   ✗ FAILED: 404 Not Found (Route not registered)" -ForegroundColor Red
    } else {
        Write-Host "   ✓ Route exists (Error: $($_.Exception.Response.StatusCode))" -ForegroundColor Green
        Write-Host "   $(  $_.Exception.Message)" -ForegroundColor Gray
    }
}
Write-Host ""

# Test 4: Docs endpoint
Write-Host "4. Testing /docs (API Documentation)" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -Method GET -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ SUCCESS - Documentation is available" -ForegroundColor Green
        Write-Host "   Open http://localhost:8000/docs in your browser to see all routes" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ✗ FAILED: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "Test complete!" -ForegroundColor Cyan
Write-Host "If you see 404 errors above, the routes are still not registered." -ForegroundColor Yellow
Write-Host "If you see other errors (422, 400, etc.), the routes ARE working!" -ForegroundColor Yellow
