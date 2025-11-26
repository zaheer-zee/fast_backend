#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Run FastAPI server
echo "Starting Crux-AI Backend..."
echo "API Documentation: http://localhost:8000/docs"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
