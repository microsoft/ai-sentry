from pydantic import BaseModel, model_validator, ValidationError, field_validator, ValidationInfo
from typing import Optional, Literal
from datetime import datetime
import re

ValidBatchStatusTypes = Literal["validating", "failed", "in_progress", "finalizing", "completed","expired", "cancelling", "cancelled"]

def check_authorisation(api_key):
    return 200

# Define Batch Object
class BatchTrackingObject(BaseModel):
    object: str = "batch"
    id: str #the id of the batch job
    endpoint: str 
    errors: dict = {
        "data": None,
        "object": 'list'
    }
    input_file_id: str # Name of the file
    completion_window: Optional[str] = '24h' #default let's say is 24h
    status: ValidBatchStatusTypes = "validating"
    output_file_id: Optional[str] = None
    error_file_id: Optional[str] = None
    created_at: str 
    in_progress_at: Optional[str] = None
    expires_at: str 
    finalizing_at: Optional[str] = None
    completed_at: Optional[str] = None
    failed_at: Optional[str] = None
    expired_at: Optional[str] = None
    cancelling_at: Optional[str] = None
    cancelled_at: Optional[str] = None
    request_counts: dict = {
        "total": None,
        "completed": None,
        "failed": None
    }
    metadata: Optional[dict] = None

    @field_validator('created_at', 'in_progress_at', 'expires_at', 'finalizing_at', 'completed_at', 'failed_at', 'expired_at','cancelling_at', 'cancelled_at')
    @classmethod
    def check_string_is_date_format(cls, v: str, info: ValidationInfo) -> str:
        iso_format = "^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,7}(Z|[+-]00:00)$"
        if not re.match(iso_format, v):
            raise ValueError(f"Invalid date format for {info.field_name}. Must be in format yyyy-MM-ddTHH:mm:ss.fffffffZ OR yyyy-MM-ddTHH:mm:ss.fffffff+00:00.")
        if not v.endswith('Z'):
            # If it ends with 'Z', it's UTC
            v=v[:-6] + 'Z'
        return v
    
    def to_dict(self):
        return self.model_dump()
    
    def to_json(self):
        return self.model_dump_json()