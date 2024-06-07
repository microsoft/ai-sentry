from flask import Flask, request, jsonify
from cloudevents.http import from_http
from requests.exceptions import HTTPError
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import AzureError
from dapr.clients import DaprClient
from utils.analyze_pii import analyze_pii_async
from utils.ai_sentry_helpers import openAISummaryLogObject
from utils.analyze_pii_chunked_ta import analyze_pii_async
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

# Set up the logger
logging.basicConfig(level=getattr(logging, log_level))
print(f"Log level is set to {log_level}")

logger = logging.getLogger(__name__)
app = Flask(__name__)
load_dotenv(".env", override=True)


app_port = os.getenv('APP_PORT', '7001')


# Register Dapr pub/sub subscriptions
@app.route('/dapr/subscribe', methods=['GET'])
def subscribe():
    subscriptions = [{
        'pubsubname': 'openaipubsub',
        'topic': 'requests-logging',
        'route': 'requestslogging'
    }]

    return jsonify(subscriptions)


# Dapr subscription in /dapr/subscribe sets up this route
@app.route('/requestslogging', methods=['POST'])
async def oairequests_subscriber():
    event = from_http(request.headers, request.get_data())
    data = json.loads(event.data)

    logger.debug(f"Received a request to log data{data}")
    
    consumer_id=data['sentry_ai_headers'].get('ai-sentry-consumer')
    model_name=data['model']
    usage_info=data['usage']
    openai_response_id=data['openai_response_id']
    date = datetime.datetime.fromisoformat(data['date_time_utc'])
    month_date = date.strftime("%m_%Y")
    
    logger.info('Consumer Product Id: %s', consumer_id)
    logger.info('ModelName: %s', model_name)
    logger.info('Usage Info: %s', usage_info)   
    log_id=f"{model_name}_{consumer_id}_{month_date}"

    summary_info = openAISummaryLogObject(id=openai_response_id, LogId=log_id, timestamp=data['date_time_utc'], model=model_name, product_id=consumer_id, usage=usage_info, month_year=month_date)
    summary_info_dict = summary_info.to_dict()

    output_binding_data = json.dumps(summary_info_dict)
       
    # Send the output to CosmosDB using Dapr binding
    with DaprClient() as d:
        resp = d.invoke_binding(
            binding_name='summary-log',
            operation='create',
            binding_metadata={
                'partitionKey': 'LogId',
            },
            data=output_binding_data
        )
   
    return json.dumps(output_binding_data), 200

app.run(port=app_port)
