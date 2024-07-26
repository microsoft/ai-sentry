import os
import json
import logging
from dotenv import load_dotenv
import httpx
import tiktoken


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv(".env", override=True)


def get_endpoints_from_poolname(poolname, json_data):
    for pool in json_data['pools']:
        if pool['name'] == poolname:
            return pool['endpoints']
    return None


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    logger.info(f"encoding_name: {encoding_name}")
    
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens



def init_endpoint_stats(pools_info):
    pool_endpoints = {}
    for pool in pools_info["pools"]:
        transformed_endpoints = []
        for endpoint in pool["endpoints"]:
            transformed_endpoints.append({
                "url": endpoint["url"],
                "x-ratelimit-remaining-requests": '10000',
                "x-ratelimit-remaining-tokens": '10000',
                "x-retry-after-ms": '0',
                "api-key": endpoint["api-key"],
                "client": httpx.AsyncClient(base_url=endpoint["url"],limits=httpx.Limits(max_keepalive_connections=None, max_connections=None)),
                "connection_errors_count": 0
            })
        pool_endpoints[pool["name"]] = transformed_endpoints
    return pool_endpoints

def select_pool(pool_endpoints, pool_name):
    return pool_endpoints.get(pool_name, None)

async def getNextAvailableEndpointInfo(open_ai_endpoint_availability_stats):
    logger.debug(f"open_ai_endpoint_availability_stats: {open_ai_endpoint_availability_stats}")
    remaining_requests = sorted(open_ai_endpoint_availability_stats ,key=lambda x: int(x['x-ratelimit-remaining-requests']), reverse=True)[0]
    remaining_tokens = sorted(open_ai_endpoint_availability_stats ,key=lambda x: int(x['x-ratelimit-remaining-tokens']), reverse=True)[0]
    logger.info(f"Next available endpoint: {remaining_requests['url']}")

    # Add a new key 'max_limit' to each dictionary that is the maximum of 'x-ratelimit-remaining-requests' and 'x-ratelimit-remaining-tokens'
    # for endpoint in open_ai_endpoint_availability_stats:
    #     endpoint['max_limit'] = max(endpoint['x-ratelimit-remaining-requests'], endpoint['x-ratelimit-remaining-tokens'])

    # Sort based on 'max_limit'
    #sorted_endpoints = sorted(open_ai_endpoint_availability_stats ,key=lambda x: x['max_limit'], reverse=True)

    # # Select the first endpoint with 'max_limit' greater than zero
    # highest_endpoint = next((endpoint for endpoint in sorted_endpoints if endpoint['max_limit'] > 0), None)

    # if highest_endpoint is not None:
    #     logger.info(highest_endpoint)
    # else:
        # logger.info("No endpoint has a max_limit greater than zero.")

    return remaining_requests






class AISentryHeaders:
    # we will check for following ai-sentry specific http headers
    # ai-sentry-consumer - just needs to be non-empty
    # ai-sentry-log-level - need to validate specific values - 

    def __init__(self):
        # Define acceptable values for each header
        self.header_values = {
            "ai-sentry-log-level": {"COMPLETE", "PII_STRIPPING_ENABLED", "DISABLED"}
        }

    def validate_headers(self, headers):
        valid_headers = {}
        required_headers = ["Ai-Sentry-Backend-Pool", "Ai-Sentry-Consumer", "Ai-Sentry-Log-Level","Ai-Sentry-Adapters"]

        # for required_header in required_headers:
        #     logger.info(f"required_header: {required_header}")
        #     if required_header not in headers:
        #         raise ValueError(f"Missing required header {required_header}")

        for header, value in headers:
            logger.debug(f"header: {header}, value: {value}")
            if header.lower() == "ai-sentry-backend-pool":
                if value == "":
                    logger.info("ai-sentry-backend-pool cannot be an empty string")
                    raise ValueError("ai-sentry-backend-pool cannot be an empty string")
                else:
                    valid_headers[header.lower()] = value
            if header.lower() == "ai-sentry-consumer":
                if value == "":
                    raise ValueError("ai-sentry-consumer cannot be an empty string")
                else:
                    valid_headers[header.lower()] = value
            if header.lower() == "ai-sentry-adapters":
                if value == "":
                    logger.info("ai-sentry-backend-adapters cannot be an empty string")
                    raise ValueError("ai-sentry-adapters cannot be an empty string")
                else:
                    valid_headers[header.lower()] = value
            elif header.lower() in self.header_values:
                if value not in self.header_values[header.lower()]:
                    raise ValueError(f"Invalid value {value} for header {header}, accepted values FULL, PII_STRIPPING_ENABLED, DISABLED")
                else:
                    valid_headers[header.lower()] = value
            # valid_headers[header] = value

        return valid_headers


  
class openAISummaryLogObject:
    def __init__(self,id, LogId, timestamp, product_id, usage, model, month_year):
        self.id = id
        self.LogId = LogId
        self.timestamp = timestamp
        self.product_id = product_id
        self.usage = usage
        self.model = model
        self.month_year = month_year
    
    def to_dict(self):
        return {
            'id': self.id,
            'LogId': self.LogId,
            'model': self.model,
            'timestamp': self.timestamp,
            'ProductId': self.product_id,
            'promptTokens': self.usage['prompt_tokens'] if self.usage is not None else None,
            'responseTokens': self.usage.get('completion_tokens', None) if self.usage is not None else None,
            'totalTokens': self.usage.get('total_tokens', None) if self.usage is not None else None ,
            'month_year': self.month_year
        }   


class openAILogObject:
    def __init__(self, date_time_utc, headers, params, request_body, response_body, sentry_ai_headers, is_Streaming, usage, model, openai_response_id):
        self.date_time_utc = date_time_utc
        self.headers = headers
        self.params = params
        self.request_body = request_body
        self.response_body = response_body
        self.sentry_ai_headers = sentry_ai_headers
        self.is_Streaming = is_Streaming
        self.usage = usage
        self.model = model
        self.openai_response_id = openai_response_id


    def to_dict(self):
        return {
            'date_time_utc': self.date_time_utc,
            'is_Streaming': self.is_Streaming,
            'headers': self.headers,
            'params': self.params,
            'request_body': self.request_body,
            'response_body': self.response_body,
            'sentry_ai_headers': self.sentry_ai_headers,
            'usage': self.usage,
            'model': self.model,
            'openai_response_id': self.openai_response_id
        }
    
class Usage:
    def __init__(self, completion_tokens=None, prompt_tokens=None, total_tokens=None):
        self.completion_tokens = completion_tokens
        self.prompt_tokens = prompt_tokens
        self.total_tokens = total_tokens

    def to_dict(self):
        return {
            'completion_tokens': self.completion_tokens,
            'prompt_tokens': self.prompt_tokens,
            'total_tokens': self.total_tokens
        }



