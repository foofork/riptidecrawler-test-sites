#!/bin/bash

# Test script for all Phase 1 sites

echo "================================================"
echo "Testing Phase 1 Sites"
echo "================================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test Site 1: happy-path.site
echo -e "\n${YELLOW}Testing Site 1: happy-path.site (Port 5001)${NC}"
cd happy-path.site
python3 -m venv venv 2>/dev/null
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
pip install -q -r requirements.txt
python app.py &
SITE1_PID=$!
sleep 2

if curl -s http://localhost:5001/ | grep -q "Happy Path Events"; then
    echo -e "${GREEN}✓ Homepage loaded${NC}"
else
    echo -e "${RED}✗ Homepage failed${NC}"
fi

if curl -s http://localhost:5001/event/1 | grep -q "schema.org"; then
    echo -e "${GREEN}✓ JSON-LD present${NC}"
else
    echo -e "${RED}✗ JSON-LD missing${NC}"
fi

if curl -s http://localhost:5001/robots.txt | grep -q "Sitemap:"; then
    echo -e "${GREEN}✓ robots.txt valid${NC}"
else
    echo -e "${RED}✗ robots.txt invalid${NC}"
fi

if curl -s http://localhost:5001/sitemap.xml | grep -q "urlset"; then
    echo -e "${GREEN}✓ sitemap.xml valid${NC}"
else
    echo -e "${RED}✗ sitemap.xml invalid${NC}"
fi

kill $SITE1_PID 2>/dev/null
deactivate 2>/dev/null
cd ..

# Test Site 2: redirects-canonical.site
echo -e "\n${YELLOW}Testing Site 2: redirects-canonical.site (Port 5005)${NC}"
cd redirects-canonical.site
python3 -m venv venv 2>/dev/null
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
pip install -q -r requirements.txt
python app.py &
SITE2_PID=$!
sleep 2

if curl -sI http://localhost:5005/redirect/301/1 | grep -q "301"; then
    echo -e "${GREEN}✓ 301 redirect works${NC}"
else
    echo -e "${RED}✗ 301 redirect failed${NC}"
fi

if curl -sI http://localhost:5005/redirect/302/1 | grep -q "302"; then
    echo -e "${GREEN}✓ 302 redirect works${NC}"
else
    echo -e "${RED}✗ 302 redirect failed${NC}"
fi

if curl -s http://localhost:5005/canonical/duplicate1 | grep -q 'rel="canonical"'; then
    echo -e "${GREEN}✓ Canonical tag present${NC}"
else
    echo -e "${RED}✗ Canonical tag missing${NC}"
fi

if curl -s http://localhost:5005/robots.txt | grep -q "User-agent:"; then
    echo -e "${GREEN}✓ robots.txt valid${NC}"
else
    echo -e "${RED}✗ robots.txt invalid${NC}"
fi

kill $SITE2_PID 2>/dev/null
deactivate 2>/dev/null
cd ..

# Test Site 3: robots-and-sitemaps.site
echo -e "\n${YELLOW}Testing Site 3: robots-and-sitemaps.site (Port 5006)${NC}"
cd robots-and-sitemaps.site
python3 -m venv venv 2>/dev/null
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
pip install -q -r requirements.txt
python app.py &
SITE3_PID=$!
sleep 2

if curl -s http://localhost:5006/robots.txt | grep -q "Crawl-delay:"; then
    echo -e "${GREEN}✓ robots.txt with crawl-delay${NC}"
else
    echo -e "${RED}✗ robots.txt invalid${NC}"
fi

if curl -s http://localhost:5006/sitemap-index.xml | grep -q "sitemapindex"; then
    echo -e "${GREEN}✓ Sitemap index valid${NC}"
else
    echo -e "${RED}✗ Sitemap index invalid${NC}"
fi

if curl -s http://localhost:5006/sitemap-blog.xml | grep -q "blog/post"; then
    echo -e "${GREEN}✓ Blog sitemap valid${NC}"
else
    echo -e "${RED}✗ Blog sitemap invalid${NC}"
fi

if curl -s http://localhost:5006/public/ | grep -q "Crawlable"; then
    echo -e "${GREEN}✓ Public page accessible${NC}"
else
    echo -e "${RED}✗ Public page failed${NC}"
fi

kill $SITE3_PID 2>/dev/null
deactivate 2>/dev/null
cd ..

echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}Phase 1 Testing Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
