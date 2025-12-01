#!/bin/bash

echo "================================================"
echo "  DEA Toolbox - Development Environment Setup  "
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

echo "✅ Python version: $(python3 --version)"
echo "✅ Node.js version: $(node --version)"
echo ""

# Backend setup
echo "📦 Setting up Backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -q -r requirements.txt

echo "✅ Backend setup complete!"
echo ""

# Frontend setup
echo "📦 Setting up Frontend..."
cd ../frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
else
    echo "Node modules already installed."
fi

echo "✅ Frontend setup complete!"
echo ""

# Start services
echo "================================================"
echo "  Starting DEA Toolbox Services  "
echo "================================================"
echo ""

cd ..

echo "🚀 Starting Backend on http://localhost:8000..."
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!

echo "🚀 Starting Frontend on http://localhost:3000..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "================================================"
echo "  DEA Toolbox is Running!  "
echo "================================================"
echo ""
echo "📍 Frontend: http://localhost:3000"
echo "📍 Backend API: http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services..."
echo ""

# Trap Ctrl+C and kill both processes
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# Wait for processes
wait
