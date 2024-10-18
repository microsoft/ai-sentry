from dotenv import load_dotenv
import os
from azure.storage.queue import QueueServiceClient
from azure.cosmos import CosmosClient, exceptions

load_dotenv(".env", override=True)

#Storage Queue configuration
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
QUEUE_NAME = os.getenv('QUEUE_NAME')

# CosmosDB configuration
COSMOS_ENDPOINT = os.getenv('COSMOS_ENDPOINT')
COSMOS_KEY = os.getenv('COSMOS_KEY')
COSMOS_DATABASE_NAME = 'batch'
COSMOS_CONTAINER_NAME = 'job_tracking'

async def send_storage_queue(batch_id, logger):
    try:
        # Create a QueueServiceClient
        queue_service_client = QueueServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        
        # Get a QueueClient
        queue_client = queue_service_client.get_queue_client(queue=QUEUE_NAME)
        
        # Send the batch_id to the queue
        queue_client.send_message(batch_id)
        
        logger.info(f"sent to queue")

        return 200
    except Exception as e:
        # logger.error(f"Failed to send batch ID to queue: {e}")
        return 500

async def send_cosmos(batch_response, logger):
    try:
        # Create cosmos client
        client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
        
        # Get the database and container
        database = client.get_database_client(COSMOS_DATABASE_NAME)
        container = database.get_container_client(COSMOS_CONTAINER_NAME)
        
        # Create or update the item in the container
        container.upsert_item(batch_response)
        
        return 200  # OK
    except exceptions.CosmosHttpResponseError as e:
        logger.error(f"Failed to send batch response to CosmosDB: {e}")
        return 500  # Internal Server Error