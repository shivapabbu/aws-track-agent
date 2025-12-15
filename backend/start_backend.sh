#!/bin/bash
# Script to start the backend with proper setup

echo "Starting AWS Track Agent Backend..."
echo ""

# Check Python version
python_version=$(python3 --version 2>&1)
echo "Python: $python_version"

# Check if we're in the backend directory
if [ ! -f "run.py" ]; then
    echo "Error: run.py not found. Please run this script from the backend directory."
    exit 1
fi

# Check dependencies
echo "Checking dependencies..."
python3 -c "import fastapi, uvicorn, boto3" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Run health check
echo ""
echo "Running health check..."
python3 check_backend.py

echo ""
echo "Starting backend server..."
python3 run.py
