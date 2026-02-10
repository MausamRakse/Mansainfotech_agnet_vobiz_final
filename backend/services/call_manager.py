import os
import random
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from livekit import api
from typing import List, Dict

# Assumes .env is in the project root
load_dotenv(".env")

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

# Project Root Directories
TRANSCRIPTS_JSON_DIR = "transcripts_json"
RECORDINGS_AUDIO_DIR = "recordings_audio"
LOGS_DIR = "logs"

class CallManager:
    @staticmethod
    async def dispatch_call(phone_number: str) -> Dict:
        """
        Dispatches a single call to the LiveKit agent.
        """
        if not phone_number.startswith("+"):
            return {"error": "Phone number must start with '+' and country code."}
            
        if not (LIVEKIT_URL and LIVEKIT_API_KEY and LIVEKIT_API_SECRET):
             return {"error": "LiveKit credentials missing in environment variables."}

        print(f"DEBUG: Dispatching call to {phone_number}...")
        print(f"DEBUG: Using LiveKit URL: {LIVEKIT_URL}")
        
        lk_api = api.LiveKitAPI(url=LIVEKIT_URL, api_key=LIVEKIT_API_KEY, api_secret=LIVEKIT_API_SECRET)
        
        # Unique Room Name
        safe_phone = phone_number.replace('+', '')
        room_name = f"call-{safe_phone}-{random.randint(1000, 9999)}"
        
        try:
            dispatch_request = api.CreateAgentDispatchRequest(
                agent_name="transcription-agent", 
                room=room_name,
                metadata=json.dumps({"phone_number": phone_number})
            )
            
            print(f"DEBUG: Sending dispatch request for room {room_name}...")
            dispatch = await lk_api.agent_dispatch.create_dispatch(dispatch_request)
            print(f"DEBUG: Dispatch successful: {dispatch}")
            
            return {
                "success": True,
                "dispatch_id": dispatch.id,
                "room_name": room_name,
                "phone_number": phone_number,
                "status": "ring_initiated",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"ERROR in dispatch_call: {e}")
            return {"success": False, "error": str(e)}
        finally:
            await lk_api.aclose()

    @staticmethod
    def get_transcripts() -> List[Dict]:
        """
        Returns a list of call transcripts from JSON files.
        """
        transcripts = []
        if not os.path.exists(TRANSCRIPTS_JSON_DIR):
            return []
            
        for filename in os.listdir(TRANSCRIPTS_JSON_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(TRANSCRIPTS_JSON_DIR, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        transcripts.append(data)
                except Exception:
                    continue
        
        # Sort by timestamp (newest first)
        transcripts.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return transcripts

    @staticmethod
    def get_recordings() -> List[Dict]:
        """
        Returns a list of audio recordings (metadata).
        """
        recordings = []
        if not os.path.exists(RECORDINGS_AUDIO_DIR):
            return []
            
        for filename in os.listdir(RECORDINGS_AUDIO_DIR):
            if filename.endswith(".wav"):
                # Extract info from filename: user_{job_id}_{timestamp}.wav
                parts = filename.replace(".wav", "").split("_")
                job_id = "unknown"
                ts = 0
                
                if len(parts) >= 3:
                     # e.g., user_jobid123_1739...
                     job_id = parts[1]
                     try:
                        ts = int(parts[-1])
                     except:
                        pass
                
                filepath = os.path.join(RECORDINGS_AUDIO_DIR, filename)
                recordings.append({
                    "filename": filename,
                    "filepath": filepath,
                    "job_id": job_id,
                    "timestamp": datetime.fromtimestamp(ts).isoformat() if ts > 0 else "Unknown",
                    "size_bytes": os.path.getsize(filepath)
                })
        
        recordings.sort(key=lambda x: x["timestamp"], reverse=True)
        return recordings

