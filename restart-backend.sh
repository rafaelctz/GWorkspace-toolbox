#!/bin/bash

echo "Stopping any existing backend processes..."
pkill -f "python.*main.py" 2>/dev/null || true

echo "Cleaning up authentication files..."
cd backend
rm -f token.json

echo "Starting backend..."
source venv/bin/activate 2>/dev/null || true
python3 main.py

echo "Backend started on http://localhost:8000"
