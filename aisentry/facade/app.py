\
import logging
import uuid
from datetime import datetime
from dapr.clients import DaprClient
from azure.identity import DefaultAzureCredential
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
import jwt
import json
from dotenv import load_dotenv
import os
import tiktoken
from utils.ai_sentry_helpers import select_pool, init_endpoint_stats, getNextAvailableEndpointInfo, AISentryHeaders, openAILogObject,Usage, num_tokens_from_string
from adapters.adapters import return_adapter

# initial setup for logging / env variable loading
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

logger = logging.getLogger(__name__)
logging.basicConfig(level=getattr(logging, log_level),
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S'
                    )
load_dotenv(".env", override=True)

logger.info("Starting Ai-Sentry Facade app")
app = Quart(__name__)


# Setup openAI Endpoints
endpoint_info = os.getenv('AI-SENTRY-ENDPOINT-CONFIG')
if endpoint_info is None:
    raise ValueError("AI-SENTRY-ENDPOINT-CONFIG environment variable is not set")


logger.debug(f"AI-SENTRY-ENDPOINT-CONFIG value: {endpoint_info}")

# Convert the JSON string back to a Python object
endpoint_data = json.loads(endpoint_info)



open_ai_endpoint_availability_stats = init_endpoint_stats(endpoint_data)
logger.info(f"Configured the following openAiEndpoints: {open_ai_endpoint_availability_stats}")

# Initialise DaprClient globally
daprClient = DaprClient()

streaming_completion_token_count=0
streaming_prompt_token_count=0
model_name=""
openai_response_id=""

@app.route('/liveness', methods=['GET'])
async def kubeliveness():
  return jsonify(message="Kubernetes Liveness check")

@app.route('/dapr/health', methods=['GET'])
async def dapr_health_check():
    return '', 200

    # Service unavailable
    # return '', 503


@app.route('/dapr/config', methods=['GET'])
async def dapr_config():
    return '', 200



@app.route('/openai/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
async def catch_all(path):
        
        # Get the original request method, headers, body and parameters
        method = request.method
        original_headers = request.headers
        params = request.args
        body = None
        body = await request.get_data()

        # Request Processed variable
        request_processed = False
        max_retries = 3
        current_retry = 0
        
        # pull out the ai-sentry specific headers - we use them further for worker processing options.
        ai_sentry_headers = AISentryHeaders()
        ai_sentry_headers_used = ai_sentry_headers.validate_headers(original_headers.items())
        logger.info(f"ai-sentry headers used: {ai_sentry_headers_used}")

        pool_name = ai_sentry_headers_used.get('ai-sentry-backend-pool', None)
        ai_sentry_adapters = ai_sentry_headers_used.get('ai-sentry-adapters', None)
        x_aisentry_correlation = ai_sentry_headers_used.get('x-aisentry-correlation', "00000000-0000-0000-0000-000000000000")
        logger.info(f"correlation id used: {x_aisentry_correlation}")

        logger.info(f"ai-sentry adapters used: {ai_sentry_adapters}")

        ai_sentry_adapters_json = json.loads(ai_sentry_adapters)
        logger.info(f"Selected pool name: {pool_name}")
        
        # Create a new set of headers that exclude the ai-sentry specific headers which we will forward onto openAI endpoints
        exclude_headers = ['host', 'content-length']+list(ai_sentry_headers_used)
        openAI_request_headers = {k: v for k, v in original_headers.items() if k.lower() not in exclude_headers}

        pool_endpoints = select_pool(open_ai_endpoint_availability_stats, pool_name)
        
        #strip api-key value if it is in use
        pool_endpoints_without_api_key = [{k: v for k, v in endpoint.items() if k != 'api-key'} for endpoint in pool_endpoints]
        logger.info(f"Selected pool: {pool_endpoints_without_api_key}")

        while not request_processed and current_retry <= max_retries:
            logger.info(f"Processing request retry#: {current_retry}")
            endpoint_info = await getNextAvailableEndpointInfo(pool_endpoints)
            client = endpoint_info["client"]


            # if openAI_request_headers.get('Api-Key') is not None:
            #     logger.info("detected use of api-key header - will use this for authentication")
            #     logger.debug(f"Swapping out api-key inside header with {endpoint_info['api-key']} value")
            #     openAI_request_headers['Api-Key'] = endpoint_info['api-key']

            if endpoint_info['api-key'] is not None:
                logger.info("No api-key header detected - will use the default api-key for authentication")
                openAI_request_headers['Api-Key'] = endpoint_info['api-key']

            else:
                logger.info("No api-key config detected - will use oAuth to talk to openAI backend services.")
                #Get Access Token from workload identity
                credential = DefaultAzureCredential()
                token = credential.get_token("https://cognitiveservices.azure.com/.default")
                openAI_request_headers['Authorization'] = f"Bearer {token.token}"

            
            decoded_body = body.decode('UTF-8').strip()
            json_body = None

            if not decoded_body:
                logger.info("Received an empty or None body")
                # Handle the empty or None body case here
                json_body = {}
            else:
                json_body = json.loads(decoded_body)

            
            object_value = json_body.get("object")

            if object_value == "assistant":
                logger.info("Detected assistant request")
                prompt_contents = None
                prompt_contents_string = None

            if 'messages' in json_body:
                prompt_contents = json_body['messages']
                prompt_contents_string = json.dumps(prompt_contents)
            
            else:
                logger.info("Messages not found in json_body, assuming the request is an embedding request")
                prompt_contents= json_body.get('input')
                prompt_contents_string = json.dumps(prompt_contents)
            
            
            
            is_stream_request = False
            if json_body.get('stream') is True:
                logger.info("Detected stream request")
                is_stream_request = True

                

            # Create a httpx Request object
            timeout = httpx.Timeout(timeout=5.0, read=60.0)

            # Apply the adapter transformation logic one by one
            for adapter in ai_sentry_adapters_json:
                logger.info(f"Applying transformation logic for adapter: {adapter}")
                try:
                    adapter_instance = return_adapter(request, adapter) 
                except Exception as e:
                    logger.error(f"({x_aisentry_correlation}) #1 Error loading adapter: {adapter} - {e}")
                    return jsonify(error=str(e)), 500
                path = adapter_instance.transform_path(path)
                method = adapter_instance.transform_method(method)
                body = adapter_instance.transform_body(body)
                params = adapter_instance.transform_query_string(params)
                openAI_request_headers = adapter_instance.transform_headers(openAI_request_headers)
                logger.info(f"Transformation logic applied for adapter: {adapter}")

            req = client.build_request(method, path, content=body, headers=openAI_request_headers, params=params, timeout=timeout)

            logger.info(f"Forwarding {method} request to {req.url}")

            # Handle streaming and non-streaming responses
            if is_stream_request:
                    try:
                        response = await client.send(req, stream=True)
                        # potentially recieve a timeout or a  HTTP > 499
                        response.raise_for_status()
                        current_retry += 1
                    
                    except httpcore.ConnectTimeout as timeout_err:
                        logger.error(f"({x_aisentry_correlation}) #2 Connection timed out: {timeout_err}")
                        return jsonify(error=str(timeout_err)), 500
                    
                    except HTTPError as http_err:
                        logger.info(f"HTTP error occurred: {http_err}")
                        if http_err.response.status_code == 429:  # 429 is the status code for Too Many Requests
                            logger.info(f"Received 429 response from endpoint, retrying next available endpoint")
                            current_retry += 1
                            endpoint_info["connection_errors_count"]+=1
                            request_processed = False
                            continue

                    except Exception as e:
                            # Connection Failures
                            logger.error(f"({x_aisentry_correlation}) #3 An unexpected error occurred: {e}")

                            if "429 Too Many Requests" in str(e):
                                logger.info(f"Received 429 response from endpoint, retrying next available endpoint")
                                current_retry += 1
                                endpoint_info["connection_errors_count"]+=1
                                request_processed = False
                                continue

                            return jsonify(error=str(e)), 500

                    
                    @stream_with_context
                    async def stream_response(response):
                        logger.info("Streaming response")

                        complete_buffered_response = []
                        global content_buffered_string
                        content_buffered = []
                        response_stream = []
                        global model_name
                        global openai_response_id
                        
                        async for line in response.aiter_lines():                        
                            yield f"{line}\r\n"
                            if line.startswith("data: "):
                                data=line[6:]
                                if data!= "[DONE]":
                                    # buffer the response - so we can calculate the token count using tiktok library
                                    complete_buffered_response.append(data)
                                    streaming_content_json = json.loads(data)
                                    logger.debug(f"Streaming content: {streaming_content_json}")
                                    model_name = streaming_content_json['model']
                                    openai_response_id= streaming_content_json['id']
                                    if streaming_content_json['choices']:
                                        delta = streaming_content_json['choices'][0]['delta']
                                        response_stream.append(streaming_content_json)
                                        
                                        if delta.get('content') is not None:
                                            content_buffered.append(delta['content'])


                        content_buffered_string = "".join(content_buffered)

                        # Calculate the token count using tiktok library
                        global streaming_completion_token_count
                        global streaming_prompt_token_count

                        streaming_completion_token_count = num_tokens_from_string(content_buffered_string, model_name)
                        streaming_prompt_token_count = num_tokens_from_string(prompt_contents_string, model_name)

                        logger.info(f"Streamed completion total Token count: {streaming_completion_token_count}")
                        logger.info(f"Streamed prompt total Token count: {streaming_prompt_token_count}")
                    try:
                        proxy_streaming_response = await make_response( stream_response(response))
                        proxy_streaming_response_body = await proxy_streaming_response.data
                        proxy_streaming_response.timeout = None
                        proxy_streaming_response.status_code = response.status_code
                        proxy_streaming_response.headers = {k: str(v) for k, v in response.headers.items()}
                    except Exception as e:
                            logger.error(f"({x_aisentry_correlation}) #4 An error occurred while streaming response: {e}")
                            return jsonify(error=str(e)), 500

                    # Record the stats for openAi endpoints
                    if proxy_streaming_response.headers.get("x-ratelimit-remaining-tokens") is not None:
                        endpoint_info["x-ratelimit-remaining-tokens"]=response.headers["x-ratelimit-remaining-tokens"]
                    else:
                        endpoint_info["x-ratelimit-remaining-tokens"]=0

                    if proxy_streaming_response.headers.get("x-ratelimit-remaining-requests") is not None:
                        endpoint_info["x-ratelimit-remaining-requests"]=response.headers["x-ratelimit-remaining-requests"]
                    else:
                        endpoint_info["x-ratelimit-remaining-tokens"]=0
                        endpoint_info["x-ratelimit-remaining-requests"]=0

                    utc_now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    request_body = json.loads(body) 

                    global model_name
                    global openai_response_id
                    global content_buffered_string

                    streamed_token_usage = Usage(streaming_completion_token_count, streaming_prompt_token_count, streaming_completion_token_count+streaming_prompt_token_count)

                    openAi_response_object = openAILogObject(date_time_utc=utc_now, 
                                                    headers=openAI_request_headers, 
                                                    params=params, 
                                                    request_body=request_body, 
                                                    response_body=json.dumps(content_buffered_string),
                                                    sentry_ai_headers=ai_sentry_headers_used,
                                                    is_Streaming=is_stream_request,
                                                    usage=streamed_token_usage.to_dict(),
                                                    model=model_name,
                                                    openai_response_id=openai_response_id
                                                    )
            
                    logger.debug(f"OpenAI response: {json.dumps(openAi_response_object.to_dict())}")
            
                    # Publish response payload to background queue for further processing (i.e. logging, PII stripping, etc)
                    try:
                        logger.info("Publishing to Dapr pub/sub")

                        dapr_pub = daprClient.publish_event(
                                    pubsub_name='openaipubsub',
                                    topic_name='requests-logging',
                                    data = json.dumps(json.dumps(openAi_response_object.to_dict())),
                                    data_content_type='application/json'
                        )

                        logger.info(f"Published to Dapr pub/sub: {dapr_pub}")
                        request_processed = True

                    except Exception as e:
                        logger.error(f"({x_aisentry_correlation}) #5 Error publishing to Dapr pub/sub: {e}")


                    return proxy_streaming_response

            else:
                    try:
                        response = await client.send(req, stream=False)
                        response.raise_for_status()

                    except Exception as e:
                        # Connection Failures
                        if response is None or response.status_code > 499:

                            logger.error(f"({x_aisentry_correlation}) #6 An unexpected error occurred: {e}")
                            # increment connection errors count for the endpoint
                            endpoint_info["connection_errors_count"]+=1
                            current_retry += 1
                            request_processed = False
                            continue
                        else:
                            logger.error(f"({x_aisentry_correlation}) #7 An unexpected error occured: {e}")

                    # If response is a 429 Increment retry count - to pick next aviable endpoint
                    if response.status_code == 429:

                        logger.info(f"Received 429 response from endpoint, retrying next available endpoint")
                        #endpoint_info["x-retry-after-ms"]=response.headers["x-retry-after-ms"]
                        current_retry += 1
                        endpoint_info["connection_errors_count"]+=1
                        request_processed = False
                        continue

                    response_body = await response.aread()
                    response_headers = {k: str(v) for k, v in response.headers.items()}
                    proxy_response = await make_response( (response_body, response.status_code, response_headers) )

                    # Process in-line workers
                    # Record the stats for openAi endpoints
                    if response.headers.get("x-ratelimit-remaining-tokens") is not None:
                        endpoint_info["x-ratelimit-remaining-tokens"]=response.headers["x-ratelimit-remaining-tokens"]
                    else:
                        endpoint_info["x-ratelimit-remaining-tokens"]=0

                    if response.headers.get("x-ratelimit-remaining-requests") is not None:
                        endpoint_info["x-ratelimit-remaining-requests"]=response.headers["x-ratelimit-remaining-requests"]
                    else:
                        endpoint_info["x-ratelimit-remaining-tokens"]=0

                    utc_now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    request_body = json_body   
                    response_json = json.loads(response_body)

                    #Extract the token count from the response
                    non_streaming_token_count = response_json.get('usage')
                    non_streaming_model = response_json.get('model')
                    non_streaming_openai_id = response_json.get('id', str(uuid.uuid4()))

                    logger.info(f"non_streaming_token_count: {non_streaming_token_count}")
                    logger.info(f"non_streaming_model: {non_streaming_model}")
        

                    openAi_response_object = openAILogObject(date_time_utc=utc_now, 
                                                    headers=openAI_request_headers, 
                                                    params=params, 
                                                    request_body=request_body, 
                                                    response_body=response_json,
                                                    sentry_ai_headers=ai_sentry_headers_used,
                                                    is_Streaming=is_stream_request,
                                                    usage=non_streaming_token_count,
                                                    model=non_streaming_model,
                                                    openai_response_id=non_streaming_openai_id)
            
                    logger.debug(f"OpenAI response: {json.dumps(openAi_response_object.to_dict())}")
            
                    # Publish response payload to background queue for further processing (i.e. logging, PII stripping, etc)
                    try:
                        logger.info("Publishing to Dapr pub/sub")
                
                        dapr_pub = daprClient.publish_event(
                                    pubsub_name='openaipubsub',
                                    topic_name='requests-logging',
                                    data = json.dumps(json.dumps(openAi_response_object.to_dict())),
                                    data_content_type='application/json'
                        )

                        logger.info(f"Published to Dapr pub/sub: {dapr_pub}")
                        request_processed = True

                    except Exception as e:
                        logger.error(f"({x_aisentry_correlation}) #8 Error publishing to Dapr pub/sub: {e}")

                    return proxy_response
        
        return jsonify(message=f"Request failed to process. Attempted to run: {current_retry},  against AI endpoint configuration unsucessfully"), 500
