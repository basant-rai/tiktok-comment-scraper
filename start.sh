#!/bin/bash

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Help function
show_help() {
    cat << EOF
${BLUE}TikTok Scraper - Start Script${NC}

${GREEN}Usage:${NC}
    ./start.sh [COMMAND] [OPTIONS]

${GREEN}Commands:${NC}
    dev              Start development environment (Docker with hot reload)
    prod             Start production environment (Docker)
    local            Start with local venv (legacy)
    build            Build Docker image
    logs             View container logs
    stop             Stop running containers
    shell            Enter container shell
    clean            Remove containers and volumes
    help             Show this help message

${GREEN}Examples:${NC}
    ./start.sh dev                    # Start dev with Docker
    ./start.sh prod                   # Start production with Docker
    ./start.sh local                  # Start with local venv
    ./start.sh logs                   # View logs
    ./start.sh stop                   # Stop containers

${GREEN}Environment Variables:${NC}
    MS_TOKEN        TikTok session token (required for scraping)
    DEBUG           Enable debug mode (default: True for dev, False for prod)
    PORT            API port (default: 5000)

${YELLOW}Note:${NC}
    Docker commands require Docker and Docker Compose to be installed.
    For production, set MS_TOKEN in your .env file before running 'prod'

EOF
}

# Check if Docker and Docker Compose are installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}✗ Docker is not installed${NC}"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}✗ Docker Compose is not installed${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"
}

# Build function
build_image() {
    echo -e "${BLUE}Building Docker image...${NC}"
    docker-compose build
    echo -e "${GREEN}✓ Build complete${NC}"
}

# Development start (Docker)
start_dev() {
    echo -e "${BLUE}🎵 TikTok Comment Scraper - Development Environment${NC}"
    echo -e "${YELLOW}Features:${NC}"
    echo "  • Hot reload on file changes"
    echo "  • API at http://localhost:5000"
    echo "  • API Docs at http://localhost:5000/docs"
    echo -e "${YELLOW}Press Ctrl+C to stop${NC}\n"

    docker-compose up
}

# Production start (Docker)
start_prod() {
    echo -e "${BLUE}🎵 TikTok Comment Scraper - Production Environment${NC}"

    # Check for MS_TOKEN
    if [ -f .env ]; then
        if grep -q "MS_TOKEN=" .env && ! grep -q "MS_TOKEN=$" .env; then
            echo -e "${GREEN}✓ MS_TOKEN is set${NC}"
        else
            echo -e "${YELLOW}⚠ Warning: MS_TOKEN is not set in .env${NC}"
            echo -e "${YELLOW}Scraping may fail without a valid token${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ No .env file found${NC}"
        echo -e "${YELLOW}Create .env with MS_TOKEN for production${NC}"
    fi

    echo -e "${YELLOW}Starting containers...${NC}"
    docker-compose -f docker-compose.prod.yml up -d

    echo -e "${GREEN}✓ Production environment started${NC}"
    echo -e "${BLUE}API available at http://localhost:5000${NC}"
    echo -e "${BLUE}View logs: ${NC}./start.sh logs"
    echo -e "${BLUE}Stop: ${NC}./start.sh stop"
}

# Development start (Local venv - legacy)
start_local() {
    echo -e "${BLUE}🎵 TikTok Comment Scraper - Local Startup Script${NC}"
    echo "=========================================="
    echo ""

    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
        python -m venv venv
    fi

    # Activate virtual environment
    echo -e "${YELLOW}🚀 Activating virtual environment...${NC}"
    source venv/bin/activate

    # Install/upgrade dependencies
    echo -e "${YELLOW}📥 Installing dependencies...${NC}"
    pip install -q -r requirements.txt

    # Create directories if they don't exist
    mkdir -p exports logs

    # Start the application
    echo ""
    echo -e "${GREEN}✅ Starting TikTok Comment Scraper with FastAPI...${NC}"
    echo -e "${BLUE}🌐 Open browser to: http://localhost:5000${NC}"
    echo -e "${BLUE}📚 API Docs: http://localhost:5000/docs${NC}"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo "=========================================="
    echo ""

    uvicorn app:app --host 127.0.0.1 --port 5000 --reload
}

# View logs
view_logs() {
    if docker-compose ps 2>/dev/null | grep -q "tiktok-scraper"; then
        echo -e "${BLUE}Development logs:${NC}"
        docker-compose logs -f tiktok-scraper
    elif docker-compose -f docker-compose.prod.yml ps 2>/dev/null | grep -q "tiktok-scraper"; then
        echo -e "${BLUE}Production logs:${NC}"
        docker-compose -f docker-compose.prod.yml logs -f tiktok-scraper
    else
        echo -e "${RED}No running containers found${NC}"
        exit 1
    fi
}

# Stop containers
stop_containers() {
    echo -e "${BLUE}Stopping containers...${NC}"

    # Check which compose file is in use
    if docker-compose ps 2>/dev/null | grep -q "tiktok-scraper"; then
        docker-compose down
        echo -e "${GREEN}✓ Development containers stopped${NC}"
    elif docker-compose -f docker-compose.prod.yml ps 2>/dev/null | grep -q "tiktok-scraper"; then
        docker-compose -f docker-compose.prod.yml down
        echo -e "${GREEN}✓ Production containers stopped${NC}"
    else
        echo -e "${YELLOW}⚠ No containers to stop${NC}"
    fi
}

# Shell access
enter_shell() {
    echo -e "${BLUE}Entering container shell...${NC}"

    if docker-compose ps 2>/dev/null | grep -q "tiktok-scraper"; then
        docker-compose exec tiktok-scraper sh
    elif docker-compose -f docker-compose.prod.yml ps 2>/dev/null | grep -q "tiktok-scraper"; then
        docker-compose -f docker-compose.prod.yml exec tiktok-scraper sh
    else
        echo -e "${RED}No running containers found${NC}"
        exit 1
    fi
}

# Clean up
clean_all() {
    echo -e "${RED}⚠ This will remove all containers and volumes${NC}"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Cleaning up...${NC}"
        docker-compose down -v 2>/dev/null || true
        docker-compose -f docker-compose.prod.yml down -v 2>/dev/null || true
        docker system prune -f
        echo -e "${GREEN}✓ Cleanup complete${NC}"
    else
        echo -e "${YELLOW}Cleanup cancelled${NC}"
    fi
}

# Main script logic
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi

    COMMAND=$1

    case $COMMAND in
        dev)
            check_docker
            start_dev
            ;;
        prod)
            check_docker
            start_prod
            ;;
        local)
            start_local
            ;;
        build)
            check_docker
            build_image
            ;;
        logs)
            view_logs
            ;;
        stop)
            stop_containers
            ;;
        shell)
            enter_shell
            ;;
        clean)
            clean_all
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}Unknown command: $COMMAND${NC}"
            echo "Run './start.sh help' for usage information"
            exit 1
            ;;
    esac
}

main "$@"
