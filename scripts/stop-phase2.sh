#!/bin/bash
# Stop all Phase 2 test sites

echo "🛑 Stopping Phase 2 Test Sites..."

# Find and kill all uvicorn processes on Phase 2 ports
kill $(lsof -t -i:5002) 2>/dev/null
kill $(lsof -t -i:5003) 2>/dev/null
kill $(lsof -t -i:5004) 2>/dev/null
kill $(lsof -t -i:5007) 2>/dev/null
kill $(lsof -t -i:5008) 2>/dev/null

echo "✅ All Phase 2 sites stopped!"
