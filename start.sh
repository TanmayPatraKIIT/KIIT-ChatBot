#!/bin/bash

echo "========================================"
echo "KIIT ChatBot - Starting Frontend"
echo "========================================"
echo ""
echo "Note: The backend requires MongoDB, Redis, and Ollama (LLM service)."
echo "These services are not available in this environment yet."
echo ""
echo "The frontend will start on port 5000."
echo "To fully run this application, you'll need to:"
echo "  1. Set up MongoDB (MONGODB_URL)"
echo "  2. Set up Redis (REDIS_URL)"
echo "  3. Configure an LLM provider (LLM_PROVIDER, LLM_BASE_URL)"
echo ""
echo "Starting frontend..."
echo "========================================"
echo ""

# Start frontend
cd frontend && npm run dev
