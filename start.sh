#!/bin/bash

# Capture the root directory
ROOT_DIR=$(pwd)

echo "========================================"
echo "KIIT ChatBot - Starting Application"
echo "========================================"
echo ""

# Check if backend dependencies are available
BACKEND_READY=true

# Check for MongoDB
if [ -z "$MONGODB_URL" ]; then
  echo "⚠️  MONGODB_URL not set - backend will not start"
  BACKEND_READY=false
fi

# Check for Redis  
if [ -z "$REDIS_URL" ]; then
  echo "⚠️  REDIS_URL not set - backend will not start"
  BACKEND_READY=false
fi

# Check for LLM configuration
if [ -z "$LLM_PROVIDER" ] || [ -z "$LLM_BASE_URL" ]; then
  echo "⚠️  LLM configuration not set - backend will not start"
  BACKEND_READY=false
fi

echo ""

if [ "$BACKEND_READY" = true ]; then
  echo "✅ Backend prerequisites found - starting both services"
  echo ""
  
  # Start backend in background
  echo "Starting FastAPI backend on port 8000..."
  cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
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
  echo "To start the backend, please configure:"
  echo "  1. MONGODB_URL - MongoDB connection string"
  echo "  2. REDIS_URL - Redis connection string"
  echo "  3. LLM_PROVIDER and LLM_BASE_URL - LLM service configuration"
  echo ""
  echo "Add these as Secrets in Replit, then restart the application."
  echo ""
  echo "Starting frontend on port 5000..."
  cd "$ROOT_DIR/frontend" && npm run dev
  
  # Return to root directory on exit
  cd "$ROOT_DIR"
fi
