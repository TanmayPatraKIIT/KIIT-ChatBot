#!/bin/bash

# Start backend in background
cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend
cd frontend && npm run dev

# If frontend exits, kill backend
kill $BACKEND_PID 2>/dev/null
