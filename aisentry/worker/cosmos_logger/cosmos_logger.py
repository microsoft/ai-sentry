from flask import Flask, request, jsonify
from cloudevents.http import from_http
from requests.exceptions import HTTPError
from azure.core.exceptions import AzureError
from dapr.clients import DaprClient
from utils.analyze_pii import analyze_pii_async
from utils.analyze_pii_openai import get_chat_pii_stripped_completion
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


load_dotenv(".env", override=True)

# Get log level from environment variable
log_level = os.getenv('LOG-LEVEL', 'INFO').upper()
logger = logging.getLogger(__name__)
app = Flask(__name__)

# Set up the loggerl 
logging.basicConfig(level=getattr(logging, log_level),
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S'
                    )



app_port = os.getenv('APP_PORT', '7000')

# This can be either OPENAI or TEXTANALYTICS
pii_stripping_service = os.getenv('PII_STRIPPING_SERVICE', 'OPENAI')

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

    response_body = data.get('response_body', None)
    
    consumer_id=data['sentry_ai_headers'].get('ai-sentry-consumer', None)
    log_level=data['sentry_ai_headers'].get('ai-sentry-log-level', None)
    model_name=data.get('model',None)
    openai_response_id=data.get('openai_response_id',None)
    date = datetime.datetime.fromisoformat(data.get('date_time_utc'))
    month_date = date.strftime("%m_%Y")
    
    logger.info('Consumer Product Id: %s', consumer_id)
    logger.info('LogId: %s', model_name)
    logger.info('LogLevel: %s', log_level)

    data['LogId']=f"{model_name}_{consumer_id}_{month_date}"
    data['id']=openai_response_id
    data['logLevel']=log_level
    
    output_binding_data = json.dumps(data)

    data = {key.lower(): value for key, value in data.items()}
   
    headers = data.get('sentry_ai_headers', None)
    
    
    if headers['ai-sentry-log-level'] == 'PII_STRIPPING_ENABLED':
        logger.info('Logging is set to PII Stripping mode')

        input_data: List[str] = []
        input_data.append(output_binding_data)
        if pii_stripping_service == 'TEXTANALYTICS':
            logger.debug(f"PII stripping service: {pii_stripping_service}")
            output_binding_data = await analyze_pii_async(input_data)
        
        #OPENAI BASED PII Stripping
        else:
            logger.debug(f"PII stripping service: {pii_stripping_service}")

            # Ensure a new event loop is created if the current one is closed
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            if loop.is_running():
                task = loop.create_task(get_chat_pii_stripped_completion(input_data))
                result = loop.run_until_complete(task)
            else:
                result = loop.run_until_complete(get_chat_pii_stripped_completion(input_data))

            print(result)
            # output_binding_data = await get_chat_pii_stripped_completion(input_data)
        
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
