#!/bin/bash

# MiniChat Setup Script
# This script sets up the complete MiniChat environment

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

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root. This is not recommended for security reasons."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Setup cancelled."
            exit 1
        fi
    fi
}

# Check system requirements
check_system() {
    print_status "Checking system requirements..."
    
    # Check OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_success "Linux detected"
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        print_success "macOS detected"
        OS="macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        print_success "Windows detected (Git Bash/WSL)"
        OS="windows"
    else
        print_warning "Unknown OS: $OSTYPE"
        OS="unknown"
    fi
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_success "Python3 found: $PYTHON_VERSION"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
        print_success "Python found: $PYTHON_VERSION"
    else
        print_error "Python is not installed"
        exit 1
    fi
    
    # Check Python version
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [[ $PYTHON_MAJOR -lt 3 ]] || [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 8 ]]; then
        print_error "Python 3.8+ is required. Found: $PYTHON_VERSION"
        exit 1
    fi
    
    # Check available memory
    if [[ "$OS" == "linux" ]]; then
        MEM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
        MEM_GB=$((MEM_KB / 1024 / 1024))
        if [[ $MEM_GB -lt 4 ]]; then
            print_warning "Low memory detected: ${MEM_GB}GB. Some models may not work."
        else
            print_success "Memory: ${MEM_GB}GB"
        fi
    fi
    
    # Check disk space
    DISK_KB=$(df . | awk 'NR==2 {print $4}')
    DISK_GB=$((DISK_KB / 1024 / 1024))
    if [[ $DISK_GB -lt 5 ]]; then
        print_warning "Low disk space: ${DISK_GB}GB. Models may not fit."
    else
        print_success "Disk space: ${DISK_GB}GB"
    fi
}

# Install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    if [[ "$OS" == "linux" ]]; then
        if command -v apt-get &> /dev/null; then
            print_status "Using apt-get (Debian/Ubuntu)"
            sudo apt-get update
            sudo apt-get install -y python3-venv python3-pip build-essential
        elif command -v yum &> /dev/null; then
            print_status "Using yum (RHEL/CentOS)"
            sudo yum install -y python3-devel python3-pip gcc
        elif command -v dnf &> /dev/null; then
            print_status "Using dnf (Fedora)"
            sudo dnf install -y python3-devel python3-pip gcc
        else
            print_warning "Unknown package manager. Please install python3-venv manually."
        fi
    elif [[ "$OS" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            print_status "Using Homebrew"
            brew install python3
        else
            print_warning "Homebrew not found. Please install Python 3 manually."
        fi
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    
    if [[ -d "venv" ]]; then
        print_warning "Virtual environment already exists"
        read -p "Remove and recreate? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
        else
            print_status "Using existing virtual environment"
            return
        fi
    fi
    
    $PYTHON_CMD -m venv venv
    print_success "Virtual environment created"
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Verify activation
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_error "Failed to activate virtual environment"
        exit 1
    fi
    
    print_success "Virtual environment activated: $VIRTUAL_ENV"
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [[ -f "requirements.txt" ]]; then
        print_status "Installing from requirements.txt..."
        pip install -r requirements.txt
    else
        print_error "requirements.txt not found"
        exit 1
    fi
    
    print_success "Python dependencies installed"
}

# Test installation
test_installation() {
    print_status "Testing installation..."
    
    # Run basic tests
    if python3 simple_test.py; then
        print_success "Basic tests passed"
    else
        print_error "Basic tests failed"
        exit 1
    fi
    
    # Try to import key modules
    python3 -c "
try:
    import torch
    print('✓ PyTorch:', torch.__version__)
except ImportError:
    print('✗ PyTorch not available')
    
try:
    import transformers
    print('✓ Transformers:', transformers.__version__)
except ImportError:
    print('✗ Transformers not available')
    
try:
    import fastapi
    print('✓ FastAPI:', fastapi.__version__)
except ImportError:
    print('✗ FastAPI not available')
"
}

# Create startup scripts
create_startup_scripts() {
    print_status "Creating startup scripts..."
    
    # Make startup script executable
    chmod +x start.sh
    
    # Create Windows batch file
    cat > start.bat << 'EOF'
@echo off
REM MiniChat Startup Script for Windows
REM Usage: start.bat [cli|web|test]

set MODE=%1
if "%MODE%"=="" set MODE=web

if "%MODE%"=="cli" (
    echo Starting CLI mode...
    python mini_chat_all_in_one.py --cli
) else if "%MODE%"=="web" (
    echo Starting web mode...
    echo Server will be available at http://localhost:8000
    python mini_chat_all_in_one.py --web
) else if "%MODE%"=="test" (
    echo Running tests...
    python test_mini_chat.py
) else (
    echo Invalid mode: %MODE%
    echo Usage: start.bat [cli^|web^|test]
    echo   cli  - Run in CLI mode
    echo   web  - Run in web mode (default)
    echo   test - Run tests
)
EOF
    
    print_success "Startup scripts created"
}

# Show next steps
show_next_steps() {
    print_success "Setup completed successfully!"
    echo
    echo "Next steps:"
    echo "==========="
    echo
    echo "1. Activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo
    echo "2. Run the application:"
    echo "   # CLI mode:"
    echo "   python3 mini_chat_all_in_one.py --cli"
    echo "   # Web mode:"
    echo "   python3 mini_chat_all_in_one.py --web"
    echo "   # Then open http://localhost:8000 in your browser"
    echo
    echo "3. Or use the startup scripts:"
    echo "   # Linux/macOS:"
    echo "   ./start.sh cli    # or ./start.sh web"
    echo "   # Windows:"
    echo "   start.bat cli     # or start.bat web"
    echo
    echo "4. For Docker:"
    echo "   docker-compose up --build"
    echo
    echo "5. Test the installation:"
    echo "   python3 test_mini_chat.py"
    echo
    echo "Happy chatting! 🚀"
}

# Main function
main() {
    print_status "MiniChat Setup Script"
    print_status "====================="
    echo
    
    check_root
    check_system
    install_system_deps
    create_venv
    activate_venv
    install_python_deps
    test_installation
    create_startup_scripts
    show_next_steps
}

# Run main function
main "$@"