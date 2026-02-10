from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import io
import shutil
import os
import aiofiles
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio

# --- Agent Integration ---
import sys
# Ensure root directory is in path to import agent.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

AGENT_AVAILABLE = False
# We now run the agent worker separately via 'python agent.py dev'

# Import our service logic
from backend.services.call_manager import CallManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("INFO: API Backend Started. Ensure 'python agent.py dev' is running for call handling.")
    yield
    # Shutdown logic if needed

app = FastAPI(title="Mansa Infotech AI Calling Platform API", lifespan=lifespan)


# Allow CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class SingleCallRequest(BaseModel):
    phone_number: str

class BulkCallRequest(BaseModel):
    phone_numbers: List[str]

# --- Endpoints ---

@app.get("/api/health")
def read_root():
    return {"status": "ok", "message": "Mansa Infotech AI Calling Platform API is running."}


@app.post("/api/upload-excel")
async def upload_excel(file: UploadFile = File(...)):
    """
    Parses an uploaded Excel/CSV file and extracts phone numbers.
    Returns a list of valid phone numbers found in columns like 'phone', 'mobile', 'contact', etc.
    """
    if not file.filename.endswith(('.xlsx', '.csv')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload .xlsx or .csv")

    contents = await file.read()
    
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse file: {str(e)}")

    # Try to find a phone number column
    possible_columns = ['phone', 'mobile', 'cell', 'contact', 'number', 'phone_number', 'phonenumber']
    phone_col = None
    
    # Case-insensitive match
    for col in df.columns:
        if col.lower() in possible_columns:
            phone_col = col
            break
            
    if not phone_col:
        # Fallback: check if any column looks like phone numbers (regex or simple check)
        # For simplicity, if no obvious column, take the first column
        phone_col = df.columns[0]
    
    # Extract and clean numbers
    numbers = df[phone_col].astype(str).tolist()
    cleaned_numbers = []
    for num in numbers:
        num = num.strip()
        if not num: continue
        # Basic cleanup: remove spaces, ensure it has some digits
        # Optional: Add '+' if missing (handled by calling logic validation usually)
        cleaned_numbers.append(num)

    return {"phone_numbers": cleaned_numbers, "total_count": len(cleaned_numbers)}

@app.post("/api/call-single")
async def call_single(request: SingleCallRequest):
    """
    Triggers a single outbound call.
    """
    result = await CallManager.dispatch_call(request.phone_number)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@app.post("/api/bulk-call")
async def bulk_call(request: BulkCallRequest):
    """
    Triggers multiple outbound calls sequentially (or parallel, simplistic loop for now).
    """
    results = []
    # In a real production app, this should be a background task (Celery/RQ)
    # For now, we'll just loop and dispatch. 
    # Warning: If list is huge, this request might timeout. 
    # Better to return "Accepted" and process in bg. 
    
    # Dispatching is fast (just an API call to LiveKit), so 100 numbers might take 30-60s.
    # We'll limit strictly for safety or use BackgroundTasks? 
    # Since we want return status, we might just do it.
    
    for phone in request.phone_numbers:
        # Check calling rate limits if necessary
        res = await CallManager.dispatch_call(phone)
        results.append({
            "phone": phone,
            "status": "dispatched" if "dispatch_id" in res else "failed", 
            "details": res
        })
        
    return {"results": results, "total_processed": len(results)}

@app.get("/api/transcripts")
async def get_transcripts():
    """Returns list of all transcripts."""
    return CallManager.get_transcripts()

@app.get("/api/recordings")
async def get_recordings():
    """Returns list of all recordings metadata."""
    return CallManager.get_recordings()

@app.get("/api/recordings/{filename}")
async def download_recording(filename: str):
    """Serves a specific recording file."""
    # Security check: filename shouldn't contain paths
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = os.path.join(CallManager.RECORDINGS_AUDIO_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(file_path, media_type="audio/wav", filename=filename)

@app.get("/api/call-status")
async def call_status():
    """Mock status endpoint for live logs."""
    # In a real app, implementation would depend on Webhooks from LiveKit
    # For now, return static or random status for UI demo
    return {"active_calls": 0, "completed_calls": len(CallManager.get_transcripts())}

# --- Static Files & Frontend Serving ---
# Mount the assets folder (JS/CSS)
app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

# Serve index.html for the root and any other path (for React Router)
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # If API path attempted but not found (404), return 404 JSON not HTML
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API Endpoint not found")

    # Serve index.html
    index_path = "frontend/dist/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend not built. Run 'npm run build' in frontend directory."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
