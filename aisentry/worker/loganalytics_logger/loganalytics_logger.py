from flask import Flask, request, jsonify
from cloudevents.http import from_http
from requests.exceptions import HTTPError
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import AzureError
from dapr.clients import DaprClient
from utils.analyze_pii import analyze_pii_async
from utils.analyze_pii_chunked_ta import analyze_pii_async
import logging
import asyncio
from dotenv import load_dotenv
import json
import requests
import os
import httpx
import uuid
from typing import List


# initial setup for logging / env variable loading
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

logger = logging.getLogger(__name__)
logging.basicConfig(level=getattr(logging, log_level),
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S'
                    )
load_dotenv(".env", override=True)

app = Flask(__name__)
app_port = os.getenv('APP_PORT', '7000')


# Register Dapr pub/sub subscriptions
@app.route('/dapr/subscribe', methods=['GET'])
def subscribe():
    subscriptions = [{
        'pubsubname': 'openaipubsub',
        'topic': 'requests-logging',
        'route': 'requestslogging'
    }]
    print('Dapr pub/sub is subscribed to: ' + json.dumps(subscriptions))
    return jsonify(subscriptions)


# Dapr subscription in /dapr/subscribe sets up this route
@app.route('/requestslogging', methods=['POST'])
async def oairequests_subscriber():
    event = from_http(request.headers, request.get_data())
    data = json.loads(event.data)


    # Implement log analytics logging logic here. DAPR has no native support for log analytics output binding
   
    return json.dumps(data), 200

app.run(port=app_port)
