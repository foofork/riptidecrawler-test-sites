#!/bin/bash
#
# Health Check Script for RipTide Test Sites
#
# Verifies that all Docker Compose services are running and responding.
#
# Usage:
#   ./scripts/health_check.sh
#   ./scripts/health_check.sh --phase 1
#   ./scripts/health_check.sh --site happy-path

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Site configurations (name:port)
declare -A PHASE1_SITES=(
    ["happy-path"]="5001"
    ["redirects-canonical"]="5005"
    ["robots-and-sitemaps"]="5006"
)

declare -A PHASE2_SITES=(
    ["slowpoke-and-retries"]="5007"
    ["selectors-vs-llm"]="5002"
    ["static-vs-headless"]="5003"
    ["auth-and-session"]="5008"
    ["pdfs-and-binaries"]="5004"
)

declare -A PHASE3_SITES=(
    ["encoding-and-i18n"]="5009"
    ["media-and-nonhtml"]="5010"
    ["anti-bot-lite"]="5011"
    ["jobs-and-offers"]="5012"
    ["websocket-stream-sink"]="5013"
)

# Base URL
BASE_URL="${BASE_URL:-http://localhost}"

# Configuration
TIMEOUT="${TIMEOUT:-5}"
RETRIES="${RETRIES:-3}"
RETRY_DELAY="${RETRY_DELAY:-2}"

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Function to print colored output
print_status() {
    local status=$1
    local message=$2

    case $status in
        "INFO")
            echo -e "${BLUE}ℹ${NC}  $message"
            ;;
        "SUCCESS")
            echo -e "${GREEN}✓${NC}  $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠${NC}  $message"
            ;;
        "ERROR")
            echo -e "${RED}✗${NC}  $message"
            ;;
    esac
}

# Function to check if a site is healthy
check_site() {
    local site_name=$1
    local port=$2
    local url="${BASE_URL}:${port}/"

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    print_status "INFO" "Checking ${site_name} on port ${port}..."

    # Try multiple times with retries
    for attempt in $(seq 1 $RETRIES); do
        # Use curl to check the site
        if curl -s -f -m "$TIMEOUT" "$url" > /dev/null 2>&1; then
            print_status "SUCCESS" "${site_name} is healthy (${url})"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
            return 0
        fi

        if [ $attempt -lt $RETRIES ]; then
            print_status "WARNING" "Attempt $attempt failed, retrying in ${RETRY_DELAY}s..."
            sleep "$RETRY_DELAY"
        fi
    done

    print_status "ERROR" "${site_name} is unhealthy after ${RETRIES} attempts (${url})"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    return 1
}

# Function to check Docker Compose services
check_docker_services() {
    print_status "INFO" "Checking Docker Compose services..."

    # Check if docker-compose is running
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_status "ERROR" "docker-compose not found. Please install Docker Compose."
        exit 1
    fi

    # Use 'docker compose' (v2) or 'docker-compose' (v1)
    local compose_cmd="docker-compose"
    if ! command -v docker-compose &> /dev/null; then
        compose_cmd="docker compose"
    fi

    # Get running services
    local running_services=$($compose_cmd ps --services --filter "status=running" 2>/dev/null || echo "")

    if [ -z "$running_services" ]; then
        print_status "WARNING" "No Docker Compose services are running"
        print_status "INFO" "Start services with: docker-compose up -d"
        return 1
    fi

    print_status "SUCCESS" "Found running services: $(echo $running_services | tr '\n' ' ')"
    return 0
}

# Function to check specific phase
check_phase() {
    local phase=$1
    local -n sites_ref=$2

    echo ""
    echo "========================================="
    echo "  Phase $phase Health Checks"
    echo "========================================="
    echo ""

    for site in "${!sites_ref[@]}"; do
        check_site "$site" "${sites_ref[$site]}"
        echo ""
    done
}

# Main script
main() {
    local phase=""
    local specific_site=""

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --phase)
                phase="$2"
                shift 2
                ;;
            --site)
                specific_site="$2"
                shift 2
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --phase <1|2|3>    Check sites for specific phase"
                echo "  --site <name>      Check specific site only"
                echo "  --help, -h         Show this help message"
                echo ""
                echo "Environment variables:"
                echo "  BASE_URL           Base URL for sites (default: http://localhost)"
                echo "  TIMEOUT            Timeout for each check in seconds (default: 5)"
                echo "  RETRIES            Number of retry attempts (default: 3)"
                echo "  RETRY_DELAY        Delay between retries in seconds (default: 2)"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done

    echo ""
    echo "========================================="
    echo "  RipTide Test Sites - Health Check"
    echo "========================================="
    echo ""

    # Check Docker services first
    check_docker_services
    echo ""

    # Check specific site if requested
    if [ -n "$specific_site" ]; then
        local found_port=""

        # Search for site in all phases
        for sites in PHASE1_SITES PHASE2_SITES PHASE3_SITES; do
            declare -n sites_array=$sites
            if [ -n "${sites_array[$specific_site]}" ]; then
                found_port="${sites_array[$specific_site]}"
                break
            fi
        done

        if [ -z "$found_port" ]; then
            print_status "ERROR" "Unknown site: $specific_site"
            exit 1
        fi

        check_site "$specific_site" "$found_port"

    # Check specific phase if requested
    elif [ -n "$phase" ]; then
        case $phase in
            1)
                check_phase "1" PHASE1_SITES
                ;;
            2)
                check_phase "2" PHASE2_SITES
                ;;
            3)
                check_phase "3" PHASE3_SITES
                ;;
            *)
                print_status "ERROR" "Invalid phase: $phase (must be 1, 2, or 3)"
                exit 1
                ;;
        esac

    # Check all sites
    else
        check_phase "1" PHASE1_SITES
        check_phase "2" PHASE2_SITES
        check_phase "3" PHASE3_SITES
    fi

    # Print summary
    echo ""
    echo "========================================="
    echo "  Summary"
    echo "========================================="
    echo ""
    echo "Total checks:  $TOTAL_CHECKS"
    echo -e "Passed:        ${GREEN}$PASSED_CHECKS${NC}"
    echo -e "Failed:        ${RED}$FAILED_CHECKS${NC}"
    echo ""

    # Exit with appropriate code
    if [ $FAILED_CHECKS -eq 0 ]; then
        print_status "SUCCESS" "All health checks passed!"
        exit 0
    else
        print_status "ERROR" "Some health checks failed."
        exit 1
    fi
}

# Run main function
main "$@"
