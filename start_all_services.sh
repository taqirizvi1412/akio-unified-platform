#!/bin/bash

echo "========================================"
echo "Starting All Akio Services"
echo "========================================"
echo

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."

if ! command_exists python3; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ from https://python.org"
    exit 1
fi

if ! command_exists node; then
    echo "ERROR: Node.js is not installed or not in PATH"
    echo "Please install Node.js from https://nodejs.org"
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Installing/updating Python dependencies..."
python3 -m pip install -r requirements_unified.txt

# Check if CRM node_modules exists
if [ ! -d "crm-integration-prototype/node_modules" ]; then
    echo "Installing CRM dependencies..."
    cd crm-integration-prototype
    npm install
    cd ..
fi

echo
echo "[1/5] Starting Email Assistant..."
if command_exists gnome-terminal; then
    gnome-terminal --title="Email Assistant" -- bash -c "cd '$SCRIPT_DIR/Email-Assistant' && python3 -m streamlit run email_assistant.py; exec bash"
elif command_exists osascript; then
    osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR/Email-Assistant' && python3 -m streamlit run email_assistant.py\""
else
    python3 -m streamlit run Email-Assistant/email_assistant.py &
fi
sleep 3

echo "[2/5] Starting Call Metrics API..."
if command_exists gnome-terminal; then
    gnome-terminal --title="Call Metrics API" -- bash -c "cd '$SCRIPT_DIR/Call-System' && python3 main.py; exec bash"
elif command_exists osascript; then
    osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR/Call-System' && python3 main.py\""
else
    cd Call-System && python3 main.py &
    cd ..
fi
sleep 3

echo "[3/5] Starting Call Metrics Dashboard..."
if command_exists gnome-terminal; then
    gnome-terminal --title="Call Dashboard" -- bash -c "cd '$SCRIPT_DIR/Call-System' && python3 -m streamlit run dashboard.py --server.port 8502; exec bash"
elif command_exists osascript; then
    osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR/Call-System' && python3 -m streamlit run dashboard.py --server.port 8502\""
else
    cd Call-System && python3 -m streamlit run dashboard.py --server.port 8502 &
    cd ..
fi
sleep 3

echo "[4/5] Starting CRM Integration..."
if command_exists gnome-terminal; then
    gnome-terminal --title="CRM Integration" -- bash -c "cd '$SCRIPT_DIR/crm-integration-prototype' && npm start; exec bash"
elif command_exists osascript; then
    osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR/crm-integration-prototype' && npm start\""
else
    cd crm-integration-prototype && npm start &
    cd ..
fi
sleep 3

echo "[5/5] Starting Unified Portal..."
if command_exists gnome-terminal; then
    gnome-terminal --title="Unified Portal" -- bash -c "cd '$SCRIPT_DIR' && python3 -m streamlit run unified_services_portal.py --server.port 8505; exec bash"
elif command_exists osascript; then
    osascript -e "tell application \"Terminal\" to do script \"cd '$SCRIPT_DIR' && python3 -m streamlit run unified_services_portal.py --server.port 8505\""
else
    python3 -m streamlit run unified_services_portal.py --server.port 8505 &
fi

echo
echo "========================================"
echo "All services are starting!"
echo "========================================"
echo
echo "Services will open in separate terminals/windows."
echo
echo "URLs:"
echo "- Unified Portal:      http://localhost:8505"
echo "- Email Assistant:     http://localhost:8501"
echo "- Call Metrics API:    http://localhost:8000"
echo "- Call Dashboard:      http://localhost:8502"
echo "- CRM Integration:     http://localhost:3000"
echo
echo "To stop all services, close each terminal window or press Ctrl+C in each."
echo

# Wait for user input before closing
read -p "Press Enter to exit..."