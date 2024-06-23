from flask import Flask, request, jsonify
from cloudevents.http import from_http
from requests.exceptions import HTTPError
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import AzureError
from dapr.clients import DaprClient
from utils.analyze_pii import analyze_pii_async
import logging
import datetime
import asyncio
from dotenv import load_dotenv
import json
import requests
import os
import httpx
import uuid
from typing import List

# Get log level from environment variable
log_level = os.getenv('LOG-LEVEL', 'INFO').upper()
logger = logging.getLogger(__name__)
app = Flask(__name__)

# Set up the loggerl 
logging.basicConfig(level=getattr(logging, log_level),
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S'
                    )



load_dotenv(".env", override=True)

app_port = os.getenv('APP_PORT', '7000')

# Register Dapr pub/sub subscriptions
@app.route('/dapr/subscribe', methods=['GET'])
def subscribe():
    subscriptions = [{
        'pubsubname': 'openaipubsub',
        'topic': 'requests-logging',
        'route': 'requestslogging'
    }]
    logger.info('Dapr pub/sub is subscribed to: ' + json.dumps(subscriptions))
    return jsonify(subscriptions)


# Dapr subscription in /dapr/subscribe sets up this route
@app.route('/requestslogging', methods=['POST'])
async def oairequests_subscriber():
    event = from_http(request.headers, request.get_data())
    data = json.loads(event.data)

    logger.debug(f"Received a request to log data{data}")

    response_body = data.get('response_body')
    
    consumer_id=data['sentry_ai_headers'].get('ai-sentry-consumer')
    model_name=data.get('model','null')
    openai_response_id=data.get('openai_response_id','null')
    date = datetime.datetime.fromisoformat(data.get('date_time_utc'))
    month_date = date.strftime("%m_%Y")
    
    logger.info('Consumer Product Id: %s', consumer_id)
    logger.info('LogId: %s', model_name)

    data['LogId']=f"{model_name}_{consumer_id}_{month_date}"
    data['id']=openai_response_id
    output_binding_data = json.dumps(data)

    data = {key.lower(): value for key, value in data.items()}
   
    headers = data['sentry_ai_headers']
    
    
    if headers['ai-sentry-log-level'] == 'PII_STRIPPING_ENABLED':
        logger.info('Logging is set to PII Stripping mode')

        input_data: List[str] = []
        input_data.append(output_binding_data)
        output_binding_data = await analyze_pii_async(input_data)
        logger.debug(f"PII stripped data: {output_binding_data}") 



    elif headers['ai-sentry-log-level'] == 'COMPLETE':
        logger.info('Logging is set to complete mode')
    
    else:
        logger.info('Logging is set to disabled mode')
        return json.dumps(output_binding_data), 200

    
    # Send the output to CosmosDB using Dapr binding
    with DaprClient() as d:
        resp = d.invoke_binding(
            binding_name='cosmosdb-log',
            operation='create',
            binding_metadata={
                'partitionKey': 'LogId',
            },
            data=output_binding_data
        )
    
    # return json.dumps(requestPayload), 200, {
    #     'ContentType': 'application/json'}
    return json.dumps(output_binding_data), 200

app.run(port=app_port)
