#!/bin/bash
# Test CORS configuration

echo "🔍 Testing CORS configuration..."
echo ""
echo "Testing OPTIONS request (preflight):"
curl -s -X OPTIONS https://todo-chatbot-phase3-backend.onrender.com/api/auth/signup \
  -H "Origin: https://todo-chatbot-phase3-frontend.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type" \
  -I | grep -i "access-control"

echo ""
echo "Testing POST request:"
curl -s -i -X POST https://todo-chatbot-phase3-backend.onrender.com/api/auth/signup \
  -H "Content-Type: application/json" \
  -H "Origin: https://todo-chatbot-phase3-frontend.vercel.app" \
  -d '{"email":"test@example.com","password":"test12345","username":"testuser"}' \
  | grep -i "access-control"

echo ""
echo "✅ If you see 'access-control-allow-origin: https://todo-chatbot-phase3-frontend.vercel.app' above, CORS is working!"
echo "❌ If header is missing, update CORS_ORIGINS on Render and wait for redeploy."
