#!/bin/bash

# MiniChat Startup Script
# Usage: ./start.sh [cli|web|test|docker]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        if ! command -v python &> /dev/null; then
            print_error "Python is not installed or not in PATH"
            exit 1
        else
            PYTHON_CMD="python"
        fi
    else
        PYTHON_CMD="python3"
    fi
    print_status "Using Python: $($PYTHON_CMD --version)"
}

# Check if virtual environment exists
check_venv() {
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        if [[ -d "venv" ]]; then
            print_warning "Virtual environment exists but not activated"
            print_status "Activating virtual environment..."
            source venv/bin/activate
        else
            print_warning "No virtual environment found"
            print_status "Creating virtual environment..."
            $PYTHON_CMD -m venv venv
            source venv/bin/activate
            print_status "Installing requirements..."
            pip install --upgrade pip
            pip install -r requirements.txt
        fi
    else
        print_success "Virtual environment is active: $VIRTUAL_ENV"
    fi
}

# Run tests
run_tests() {
    print_status "Running tests..."
    $PYTHON_CMD test_mini_chat.py
}

# Run CLI mode
run_cli() {
    print_status "Starting CLI mode..."
    $PYTHON_CMD mini_chat_all_in_one.py --cli
}

# Run web mode
run_web() {
    print_status "Starting web mode..."
    print_status "Server will be available at http://localhost:8000"
    $PYTHON_CMD mini_chat_all_in_one.py --web
}

# Run Docker mode
run_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    print_status "Starting with Docker..."
    docker-compose up --build
}

# Main function
main() {
    local mode=${1:-web}
    
    print_status "MiniChat Startup Script"
    print_status "Mode: $mode"
    
    case $mode in
        "cli")
            check_python
            check_venv
            run_cli
            ;;
        "web")
            check_python
            check_venv
            run_web
            ;;
        "test")
            check_python
            check_venv
            run_tests
            ;;
        "docker")
            run_docker
            ;;
        *)
            print_error "Invalid mode: $mode"
            echo "Usage: $0 [cli|web|test|docker]"
            echo "  cli    - Run in CLI mode"
            echo "  web    - Run in web mode (default)"
            echo "  test   - Run tests"
            echo "  docker - Run with Docker"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"