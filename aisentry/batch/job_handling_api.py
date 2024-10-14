import logging
import uuid
from datetime import datetime, timedelta
from dapr.clients import DaprClient
import httpcore
from enum import Enum
from typing import Tuple
from quart import Quart, jsonify, request, make_response
from quart.helpers import stream_with_context
from urllib.request import urlopen
from urllib.parse import urljoin
from datetime import datetime, timezone
import httpx
from requests.exceptions import HTTPError
import json
from dotenv import load_dotenv
import os
from batch_helpers import check_authorisation, BatchTrackingObject
from temporary_batch_methods import send_cosmos, send_storage_queue


load_dotenv(".env", override=True)

# Get log level from environment variable
log_level = os.getenv('LOG-LEVEL', 'INFO').upper()
logger = logging.getLogger(__name__)
app = Quart(__name__)

# Set up the loggerl 
logging.basicConfig(level=getattr(logging, log_level),
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S'
                    )

app_port = os.getenv('APP_PORT', '5000')

#Assume file is already in storage and input_file_id is the Azure Storage Path
@app.route('/batches', methods=['POST'])
async def create_batch_job():
    try:
        # Get headers, parameters and body
        headers = request.headers #wouldn't expect headers outside of the POST
        params = request.args

        body = None
        body = await request.get_data()

        # log the headers
        logger.info(f"Headers used: {headers}")

        # check authorisation
        api_key = headers.get('api-key')
        auth_status = check_authorisation(api_key)
        if auth_status != 200:
            return jsonify({"error": "Unauthorized"}), auth_status

        # Decode the bytes object to a string and parse it as JSON
        body = json.loads(body.decode('utf-8'))
        
        # Extract the required fields from the JSON data
        input_file_id = body.get("input_file_id")
        endpoint = body.get("endpoint")
        completion_window = body.get("completion_window")
        metadata = body.get("metadata")
        
        # Log the received data
        logger.info(f"Received request on /batches with input_file_id: {input_file_id}, endpoint: {endpoint}, completion_window: {completion_window}, metadata: {metadata}")
        
        # Generate timestamps
        created_at = datetime.now(timezone.utc)
        try:
            value, unit = completion_window[:-1], completion_window[-1]

            value = int(value)
            if unit != "h":
                raise ValueError("Unsupported time unit in completion_window")

            expires_at = created_at + timedelta(hours=value)  # Assuming completion_window is 24, but would change
        except:
            raise ValueError("Invalid format for completion window. Must be defined in hours e.g. 12h, 24h")

        # Generate a unique batch ID
        batch_id = f"batch_{uuid.uuid4()}"
        
        # Construct the response dictionary
        # add metadata
        batch_response = BatchTrackingObject(
            completion_window=completion_window,
            created_at=created_at.isoformat(),
            endpoint=endpoint,
            expires_at=expires_at.isoformat(),
            id=batch_id,
            input_file_id=input_file_id,
            status='validating',
            metadata= metadata
        )
        
        # # send response to CosmosDB
        # with DaprClient() as d:
        #     d.invoke_binding(
        #         binding_name='cosmosdb-batch', #Need to create this
        #         operation='create',
        #         binding_metadata={
        #             'partitionKey': 'id',
        #         },
        #         data=batch_response
        #     )

        # logger.info(f"Updated batch job info in CosmosDB via Dapr")

        # # send batch_id to queue
        # with DaprClient() as d:
        #     d.invoke_binding(
        #         name='azure-storage', #Need to create this
        #         operation='create',
        #         data=batch_id.encode('utf-8')
        #     )
        
        # logger.info(f"Batch ID {batch_id} sent to queue for processing via Dapr")
        
        cosmos_response = send_cosmos(batch_response, logger)
        if cosmos_response != 200:
            return jsonify({"error": "Failed to upload to cosmos"}), 500
        logger.info(f"Updated batch job info in CosmosDB")

        queue_response = send_storage_queue(batch_id, logger)
        if queue_response != 200:
            return jsonify({"error": "Failed to upload to queue"}), 500
        logger.info(f"Sent batch id to queue for processing")

        # want to log batch request as well?

        # Return the response
        return batch_response.to_json(), 201
    
    except Exception as e:
        logger.error(f"Error processing batch request: {e}")
        return jsonify({"error": "Failed to process batch request"}), 500

#Check status of batch job
# could even combine with create_batch_job?
@app.route('/batches/<string:batch_id>', methods=['GET'])
async def track_batch_job(batch_id):
    try:
        # Get headers, parameters and body
        original_headers = request.headers
        params = request.args

        return 200
    except:
        logger.info(f"Error retrieving batch request")


if __name__ == '__main__':
    app.run(port=app_port, debug=True)