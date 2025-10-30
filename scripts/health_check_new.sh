#!/bin/bash
# Health Check Script for RipTide Test Sites

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BASE_URL=${BASE_URL:-http://localhost}
MAX_RETRIES=${MAX_RETRIES:-30}
RETRY_DELAY=${RETRY_DELAY:-2}

declare -A SITES=(
    ["happy-path"]=5001
    ["selectors-vs-llm"]=5002
    ["static-vs-headless"]=5003
    ["pdfs-and-binaries"]=5004
    ["redirects-canonical"]=5005
    ["robots-and-sitemaps"]=5006
    ["slowpoke-and-retries"]=5007
    ["auth-and-session"]=5008
)

WAIT_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --wait|-w) WAIT_MODE=true; shift ;;
        --help|-h) echo "Usage: $0 [--wait]"; exit 0 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

check_service() {
    local port=$2
    curl -f -s -o /dev/null --max-time 5 "${BASE_URL}:${port}/" 2>/dev/null
}

echo "╔════════════════════════════════════════════╗"
echo "║   RipTide Test Sites - Health Check       ║"
echo "╚════════════════════════════════════════════╝"

for attempt in $(seq 1 $MAX_RETRIES); do
    all_healthy=true
    healthy_count=0

    echo -e "\n${YELLOW}Attempt $attempt/$MAX_RETRIES${NC}"

    for site in "${!SITES[@]}"; do
        port=${SITES[$site]}
        if check_service "$site" "$port"; then
            echo -e "  ${GREEN}✓${NC} $site (port $port)"
            ((healthy_count++))
        else
            echo -e "  ${RED}✗${NC} $site (port $port)"
            all_healthy=false
        fi
    done

    if [ "$all_healthy" = true ]; then
        echo -e "\n${GREEN}✅ All ${#SITES[@]} services healthy!${NC}\n"
        exit 0
    fi

    [ "$WAIT_MODE" = true ] && [ $attempt -lt $MAX_RETRIES ] && sleep $RETRY_DELAY
done

echo -e "\n${RED}❌ Some services unhealthy${NC}\n"
exit 1
