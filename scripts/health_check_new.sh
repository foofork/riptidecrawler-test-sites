#!/bin/bash
# Health Check Script for RipTide Test Sites

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BASE_URL=${BASE_URL:-http://localhost}
MAX_RETRIES=${MAX_RETRIES:-30}
RETRY_DELAY=${RETRY_DELAY:-2}

# Site definitions: port|name
SITES=(
    "5001|happy-path"
    "5002|redirects-canonical"
    "5003|robots-and-sitemaps"
    "5004|slowpoke-and-retries"
    "5005|selectors-vs-llm"
    "5006|static-vs-headless"
    "5007|pdfs-and-binaries"
    "5008|auth-and-session"
    "5009|encoding-and-i18n"
    "5010|media-and-nonhtml"
    "5011|anti-bot-lite"
    "5012|jobs-and-offers"
    "5013|websocket-stream-sink"
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
    local port=$1
    curl -f -s -o /dev/null --max-time 5 "${BASE_URL}:${port}/health" 2>/dev/null
    return $?
}

echo "╔════════════════════════════════════════════╗"
echo "║   RipTide Test Sites - Health Check       ║"
echo "╚════════════════════════════════════════════╝"

for attempt in $(seq 1 $MAX_RETRIES); do
    all_healthy=true
    healthy_count=0
    total_sites=${#SITES[@]}

    echo -e "\n${YELLOW}Attempt $attempt/$MAX_RETRIES${NC}"

    for site_def in "${SITES[@]}"; do
        IFS='|' read -r port name <<< "$site_def"

        if check_service "$port"; then
            echo -e "  ${GREEN}✓${NC} $name (port $port)"
            healthy_count=$((healthy_count + 1))
        else
            echo -e "  ${RED}✗${NC} $name (port $port)"
            all_healthy=false
        fi
    done

    if [ "$all_healthy" = "true" ]; then
        echo -e "\n${GREEN}✅ All $total_sites services healthy!${NC}\n"
        exit 0
    fi

    echo -e "  ${YELLOW}Status: $healthy_count/$total_sites services healthy${NC}"

    if [ "$WAIT_MODE" = "true" ] && [ $attempt -lt $MAX_RETRIES ]; then
        sleep $RETRY_DELAY
    elif [ "$WAIT_MODE" != "true" ]; then
        break
    fi
done

echo -e "\n${RED}❌ Some services unhealthy after $MAX_RETRIES attempts${NC}\n"
exit 1
