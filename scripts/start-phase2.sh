#!/bin/bash
# Start all Phase 2 test sites

echo "🚀 Starting Phase 2 Test Sites..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Site 1: Selectors vs LLM (Port 5002)
echo -e "${BLUE}Starting selectors-vs-llm.site on port 5002...${NC}"
cd sites/selectors-vs-llm.site
pip install -q -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 5002 > /dev/null 2>&1 &
PID1=$!
cd ../..

# Site 2: Static vs Headless (Port 5003)
echo -e "${BLUE}Starting static-vs-headless.site on port 5003...${NC}"
cd sites/static-vs-headless.site
pip install -q -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 5003 > /dev/null 2>&1 &
PID2=$!
cd ../..

# Site 3: Slowpoke and Retries (Port 5007)
echo -e "${BLUE}Starting slowpoke-and-retries.site on port 5007...${NC}"
cd sites/slowpoke-and-retries.site
pip install -q -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 5007 > /dev/null 2>&1 &
PID3=$!
cd ../..

# Site 4: Auth and Session (Port 5008)
echo -e "${BLUE}Starting auth-and-session.site on port 5008...${NC}"
cd sites/auth-and-session.site
pip install -q -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 5008 > /dev/null 2>&1 &
PID4=$!
cd ../..

# Site 5: PDFs and Binaries (Port 5004)
echo -e "${BLUE}Starting pdfs-and-binaries.site on port 5004...${NC}"
cd sites/pdfs-and-binaries.site
pip install -q -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 5004 > /dev/null 2>&1 &
PID5=$!
cd ../..

# Wait for all sites to start
sleep 3

echo ""
echo -e "${GREEN}✅ All Phase 2 sites started!${NC}"
echo ""
echo "📋 Phase 2 Test Sites:"
echo "  1. Selectors vs LLM:       http://localhost:5002"
echo "  2. Static vs Headless:     http://localhost:5003"
echo "  3. Slowpoke and Retries:   http://localhost:5007"
echo "  4. Auth and Session:       http://localhost:5008"
echo "  5. PDFs and Binaries:      http://localhost:5004"
echo ""
echo "Process IDs: $PID1 $PID2 $PID3 $PID4 $PID5"
echo ""
echo "To stop all sites, run:"
echo "  kill $PID1 $PID2 $PID3 $PID4 $PID5"
echo ""
echo "Or use: ./scripts/stop-phase2.sh"
