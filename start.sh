#!/bin/bash

# Capture the root directory
ROOT_DIR=$(pwd)

echo "========================================"
echo "KIIT ChatBot - Starting Application"
echo "========================================"
echo ""

# Check if backend dependencies are available
BACKEND_READY=true

# Check for PostgreSQL (DATABASE_URL should be set by Replit)
if [ -z "$DATABASE_URL" ]; then
  echo "⚠️  DATABASE_URL not set - backend will not start"
  BACKEND_READY=false
fi

# Check for OpenAI (via Replit AI Integrations)
if [ -z "$AI_INTEGRATIONS_OPENAI_API_KEY" ]; then
  echo "⚠️  OpenAI integration not configured - backend will not start"
  BACKEND_READY=false
fi

echo ""

if [ "$BACKEND_READY" = true ]; then
  echo "✅ Backend prerequisites found - starting both services"
  echo ""
  
  # Start backend in background
  echo "Starting FastAPI backend on port 8000..."
  cd "$ROOT_DIR/backend" && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
  BACKEND_PID=$!
  
  # Wait for backend to initialize
  sleep 5
  
  # Start frontend
  echo "Starting Next.js frontend on port 5000..."
  cd "$ROOT_DIR/frontend" && npm run dev
  
  # If frontend exits, kill backend and return to root
  cd "$ROOT_DIR"
  kill $BACKEND_PID 2>/dev/null
else
  echo "⚠️  Backend prerequisites missing - starting frontend only"
  echo ""
  echo "Note: Backend is configured to use:"
  echo "  ✅ PostgreSQL (Replit built-in database)"
  echo "  ✅ OpenAI via Replit AI Integrations (no API key needed)"
  echo "  ✅ In-memory caching (no Redis required)"
  echo ""
  echo "The OpenAI integration should be set up automatically."
  echo "If you see this message, please restart the application."
  echo ""
  echo "Starting frontend on port 5000..."
  cd "$ROOT_DIR/frontend" && npm run dev
  
  # Return to root directory on exit
  cd "$ROOT_DIR"
fi
