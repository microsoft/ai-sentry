from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

ValidBatchStatusTypes = Literal["validating", "failed", "in_progress", "finalizing", "completed","expired", "cancelling", "cancelled"]

def check_authorisation(api_key):
    return 200

# Define Batch Object
class BatchTrackingObject(BaseModel):
    object: str = "batch"
    id: str #= None #the id of the batch job
    endpoint: str 
    errors: dict = {
        "data": None,
        "object": 'list'
    }
    input_file_id: str #= None # Name of the file
    completion_window: Optional[str] = '24h' #default let's say is 24h
    status: ValidBatchStatusTypes = "validating"
    output_file_id: Optional[str] = None
    error_file_id: Optional[str] = None
    created_at: datetime # = None
    in_progress_at: Optional[datetime] = None
    expires_at: datetime #Optional[datetime] = None
    finalizing_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    cancelling_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    request_counts: dict = {
        "total": None,
        "completed": None,
        "failed": None
    }
    metadata: Optional[dict] = None
    
    def to_dict(self):
        return self.model_dump()
    
    def to_json(self):
        return self.model_dump_json()