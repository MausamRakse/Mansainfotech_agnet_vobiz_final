from pydantic import BaseModel
from typing import List, Optional

class PhoneNumber(BaseModel):
    phone_number: str

class BulkCallRequest(BaseModel):
    phone_numbers: List[str]

class CallStatusResponse(BaseModel):
    room_name: str
    dispatch_id: str
    phone_number: str
    status: str
    timestamp: str

class TranscriptModel(BaseModel):
    job_id: str
    phone_number: str
    timestamp: str
    content: List[dict] # JSON content

class RecordingModel(BaseModel):
    file_name: str
    path: str
    timestamp: str
