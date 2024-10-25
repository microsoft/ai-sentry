from pydantic import BaseModel, model_validator, ValidationError, field_validator, ValidationInfo
from typing import Optional, Literal
from datetime import datetime
import json
import re
from dotenv import load_dotenv
import os
# from azure.storage.queue import QueueServiceClient
from azure.cosmos import CosmosClient, exceptions

load_dotenv(".env", override=True)

# CosmosDB configuration
COSMOS_ENDPOINT = os.getenv('COSMOS_ENDPOINT')
COSMOS_KEY = os.getenv('COSMOS_KEY')
COSMOS_DATABASE_NAME = 'batch'
COSMOS_CONTAINER_NAME = 'job_tracking'

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
    

async def send_to_cosmos(body, logger):
    try:
        # Create cosmos client
        client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
        
        # Get the database and container
        database = client.get_database_client(COSMOS_DATABASE_NAME)
        container = database.get_container_client(COSMOS_CONTAINER_NAME)
        
        # Create or update the item in the container
        container.upsert_item(body)
        
        return 200  # OK
    except exceptions.CosmosHttpResponseError as e:
        logger.error(f"Failed to send to CosmosDB: {e}")
        return 500  # Internal Server Error
    
async def retrieve_item_from_cosmos(item_id):
    try:
        # Create cosmos client
        client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
        
        # Get the database and container
        database = client.get_database_client(COSMOS_DATABASE_NAME)
        container = database.get_container_client(COSMOS_CONTAINER_NAME)
        
        # Read item in the container
        item = container.read_item(item=item_id, partition_key=item_id)
        
        return item, 200  # OK
    except exceptions.CosmosResourceNotFoundError:
        # logger.error(f"Item with id {item_id} not found.")
        return f"Item with id {item_id} not found.", 404  # Not Found
    except exceptions.CosmosHttpResponseError as e:
        # logger.error(f"Failed to send to CosmosDB: {e}")
        return f"Failed to upload to cosmos: {e}", 500  # Internal Server Error