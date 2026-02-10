#!/bin/bash

# Suppress ONNX runtime logging (removes GPU discovery warnings)
export ORT_LOGGING_LEVEL=3

# Start the LiveKit Agent in the background
# We remove the invalid --http-server-port flag. 
# The agent will use its default internal port for health checks (typically 8081)
python agent.py start &

# Start the FastAPI Backend
# binding to 0.0.0.0 and the port Render provides
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
