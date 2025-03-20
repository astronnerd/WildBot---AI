#!/bin/bash
# ------------------------------------------------------------------
# WildBot Auto-Setup & Run Script
# This script:
#   1. Kills any process using backend (port 5000) and frontend (port 3000).
#   2. Checks for (or creates) the backend virtual environment,
#      installs Python requirements, and starts the Flask backend.
#   3. Checks for (or installs) npm dependencies for the frontend,
#      and starts the React app.
# ------------------------------------------------------------------

# Function to kill a process running on a given port
kill_process_on_port() {
  PORT=$1
  PID=$(lsof -t -i:$PORT)
  if [ ! -z "$PID" ]; then
    echo "Killing process on port $PORT (PID: $PID)..."
    kill -9 $PID
    sleep 2
  fi
}

# ----------- Kill Existing Processes -----------
echo "===== Checking for existing processes ====="
kill_process_on_port 5000  # Kill backend process
kill_process_on_port 3000  # Kill frontend process

# ----------- Backend Setup -----------
echo "===== Setting up Backend ====="
cd backend || { echo "Backend folder not found!"; exit 1; }

# Create virtual environment if it doesn't exist
# if [ ! -d "venv" ]; then
#   echo "Creating virtual environment..."
#   python3 -m venv venv
# fi

# Activate virtual environment
# echo "Activating virtual environment..."
# source venv/bin/activate

# Install required Python packages
# echo "Installing Python requirements..."
# pip install -r requirements.txt

# Start Flask backend in background
echo "Starting Flask backend..."
# python3 app.py &
# BACKEND_PID=$!
# echo "Flask backend started with PID $BACKEND_PID"

# Ensure backend is stopped on script exit
cleanup() {
  echo "Stopping backend process (PID: $BACKEND_PID)..."
  kill -9 $BACKEND_PID 2>/dev/null
}
trap cleanup EXIT

# Return to project root
cd ..

# Wait a few seconds to ensure the backend is up
echo "Waiting for backend to initialize..."
sleep 5

# ----------- Frontend Setup -----------
echo "===== Setting up Frontend ====="
cd frontend || { echo "Frontend folder not found!"; exit 1; }

# Check if node_modules exists; if not, install npm dependencies
# if [ ! -d "node_modules" ]; then
#   echo "Installing npm dependencies..."
#   npm install
# fi

# Start React frontend
echo "Starting React frontend..."
npm start
