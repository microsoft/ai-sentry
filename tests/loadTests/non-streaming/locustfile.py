from locust import HttpUser, task, between
import json, os
from dotenv import load_dotenv

load_dotenv(".env", override=True)

azure_endpoint = os.getenv("azure_endpoint", "http://20.11.111.242/"), 
api_key=os.getenv("api_key", "defaultKey"),  
api_version=os.getenv("api_version", "2023-07-01-preview"),
aoai_deployment_name = os.getenv("aoai_deployment_name", "chat"),
ai_sentry_consumer = os.getenv("ai-sentry-consumer", "locustloadtest"),
ai_sentry_backend_pool = os.getenv("ai-sentry-backend-pool", "pool1"),
ai_sentry_log_level = os.getenv("ai-sentry-log-level", "COMPLETE")

# Non-Streaming Load Test
class OpenAIUser(HttpUser):
    host = azure_endpoint
    wait_time = between(1, 2.5)

    headers = {
        "Content-Type": "application/json",
        "ai-sentry-consumer": "locustloadtest",
        "ai-sentry-backend-pool":"pool1",
        "ai-sentry-adapters":"[\"SampleApiRequestTransformer\"]",
        "ai-sentry-log-level": ai_sentry_log_level,
        "api-key": "\"{}\"".format(api_key)

    }

    body = {
        "messages": [
            {
                "role": "system",
                "content": "You are an AI assistant that helps people find information."
            },
            {
                "role": "user",
                "content": "What is Microsoft's most profitable business?"
            }
        ],
        "max_tokens": 800,
        "temperature": 0.7,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "top_p": 0.95,
        "stop": None
    }

    @task
    def post_openai(self):
        self.client.post(f"openai/deployments/chat/chat/completions?api-version=2024-02-15-preview", data=json.dumps(self.body), headers=self.headers)