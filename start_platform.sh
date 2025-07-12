#!/bin/bash

echo "========================================"
echo "Starting Akio Unified Platform"
echo "========================================"
echo

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python is installed
if ! command_exists python3; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ from https://python.org"
    exit 1
fi

# Check if Node.js is installed
if ! command_exists node; then
    echo "ERROR: Node.js is not installed or not in PATH"
    echo "Please install Node.js from https://nodejs.org"
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Install Python dependencies if needed
echo "Checking Python dependencies..."
python3 -m pip install -r requirements_unified.txt

# Check if CRM node_modules exists
if [ ! -d "crm-integration-prototype/node_modules" ]; then
    echo "Installing CRM dependencies..."
    cd crm-integration-prototype
    npm install
    cd ..
fi

# Start the unified platform
echo
echo "Starting Unified Platform Dashboard..."
echo
echo "The dashboard will open in your browser at http://localhost:8501"
echo
echo "Press Ctrl+C to stop all services"
echo

python3 -m streamlit run unified_platform.py