#!/bin/bash

# Interview Feedback System - Docker Deployment Script
# This script builds and runs the interview analyzer in Docker

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="interview-analyzer"
CONTAINER_NAME="interview-analyzer-app"
VERSION="${VERSION:-latest}"

# Functions
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_env_file() {
    if [ ! -f .env ]; then
        print_warning ".env file not found!"
        echo "Please create a .env file with your API keys."
        echo "You can copy .env.example and fill in your keys:"
        echo "  cp .env.example .env"
        echo ""
        read -p "Do you want to continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_info ".env file found"
    fi
}

build_image() {
    print_info "Building Docker image: ${IMAGE_NAME}:${VERSION}"
    docker build -t ${IMAGE_NAME}:${VERSION} .

    if [ $? -eq 0 ]; then
        print_info "Image built successfully!"
    else
        print_error "Failed to build image"
        exit 1
    fi
}

stop_existing_container() {
    if [ "$(docker ps -q -f name=${CONTAINER_NAME})" ]; then
        print_info "Stopping existing container..."
        docker stop ${CONTAINER_NAME}
    fi

    if [ "$(docker ps -aq -f name=${CONTAINER_NAME})" ]; then
        print_info "Removing existing container..."
        docker rm ${CONTAINER_NAME}
    fi
}

run_container() {
    print_info "Starting container: ${CONTAINER_NAME}"

    # Check if .env exists for passing to container
    if [ -f .env ]; then
        docker run -d \
            --name ${CONTAINER_NAME} \
            --env-file .env \
            -v $(pwd)/data:/app/data \
            ${IMAGE_NAME}:${VERSION}
    else
        docker run -d \
            --name ${CONTAINER_NAME} \
            -v $(pwd)/data:/app/data \
            ${IMAGE_NAME}:${VERSION}
    fi

    if [ $? -eq 0 ]; then
        print_info "Container started successfully!"
    else
        print_error "Failed to start container"
        exit 1
    fi
}

run_interactive() {
    print_info "Running container in interactive mode..."

    if [ -f .env ]; then
        docker run -it --rm \
            --name ${CONTAINER_NAME}-interactive \
            --env-file .env \
            -v $(pwd)/data:/app/data \
            ${IMAGE_NAME}:${VERSION} \
            /bin/bash
    else
        docker run -it --rm \
            --name ${CONTAINER_NAME}-interactive \
            -v $(pwd)/data:/app/data \
            ${IMAGE_NAME}:${VERSION} \
            /bin/bash
    fi
}

run_example() {
    print_info "Running example usage..."

    if [ -f .env ]; then
        docker run -it --rm \
            --name ${CONTAINER_NAME}-example \
            --env-file .env \
            -v $(pwd)/data:/app/data \
            ${IMAGE_NAME}:${VERSION} \
            python example_usage.py
    else
        docker run -it --rm \
            --name ${CONTAINER_NAME}-example \
            -v $(pwd)/data:/app/data \
            ${IMAGE_NAME}:${VERSION} \
            python example_usage.py
    fi
}

show_logs() {
    print_info "Showing container logs..."
    docker logs -f ${CONTAINER_NAME}
}

show_usage() {
    cat << EOF
Usage: ./deploy.sh [COMMAND]

Commands:
    build           Build the Docker image
    run             Build and run the container in detached mode
    interactive     Run container with interactive shell
    example         Run the example usage script
    stop            Stop the running container
    logs            Show container logs
    clean           Stop and remove container and image
    help            Show this help message

Environment Variables:
    VERSION         Docker image version tag (default: latest)

Examples:
    ./deploy.sh build
    ./deploy.sh run
    VERSION=v1.0 ./deploy.sh build
    ./deploy.sh interactive
EOF
}

# Main script logic
case "${1}" in
    build)
        check_env_file
        build_image
        ;;
    run)
        check_env_file
        build_image
        stop_existing_container
        run_container
        print_info "Container is running. Use './deploy.sh logs' to view output"
        ;;
    interactive)
        check_env_file
        build_image
        run_interactive
        ;;
    example)
        check_env_file
        build_image
        run_example
        ;;
    stop)
        stop_existing_container
        print_info "Container stopped"
        ;;
    logs)
        show_logs
        ;;
    clean)
        stop_existing_container
        print_info "Removing Docker image..."
        docker rmi ${IMAGE_NAME}:${VERSION} 2>/dev/null || true
        print_info "Cleanup complete"
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: ${1}"
        echo ""
        show_usage
        exit 1
        ;;
esac

exit 0
