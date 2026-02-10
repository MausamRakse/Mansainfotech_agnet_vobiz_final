#!/bin/bash

# Suppress ONNX runtime logging (removes GPU discovery warnings)
export ORT_LOGGING_LEVEL=3

# Start the LiveKit Agent in the background
# We use --dev to avoid some production check constraints if needed, 
# but for Render 'start' is usually correct.
# We set the health check port to something else to avoid Render's auto-detection confusion
python agent.py start --http-server-port 8081 &

# Start the FastAPI Backend
# binding to 0.0.0.0 and the port Render provides
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
