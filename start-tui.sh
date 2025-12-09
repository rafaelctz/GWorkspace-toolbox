#!/bin/bash

echo "================================================"
echo "   GWorkspace Toolbox - Terminal Interface    "
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

echo "✅ Python version: $(python3 --version)"
echo ""

# Check if backend is running
echo "🔍 Checking backend status..."
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "⚠️  Backend is not running!"
    echo "   Please start the backend first:"
    echo "   ./start-dev.sh"
    echo ""
    read -p "Do you want to start the TUI anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "================================================"
echo "         Starting TUI Application             "
echo "================================================"
echo ""
echo "Controls:"
echo "  - Navigate: Arrow keys or Tab"
echo "  - Select: Enter"
echo "  - Back: ESC"
echo "  - Quit: Q or ESC on main screen"
echo ""

# Activate venv and run TUI
cd backend
source venv/bin/activate
cd ..
python3 tui.py "$@"
