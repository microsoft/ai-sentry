from locust import HttpUser, task, between
import json, os
from dotenv import load_dotenv

load_dotenv(".env", override=True)

azure_endpoint = os.getenv("azure_endpoint", "http://ai-sentry-url/"), 
api_key=os.getenv("api_key", "defaultkey"),  
api_version=os.getenv("api_version", "2023-07-01-preview"),
aoai_deployment_name = os.getenv("aoai_deployment_name", "chat")

# Non-Streaming Load Test
class OpenAIUser(HttpUser):
    host = azure_endpoint
    wait_time = between(1, 2.5)

    headers = {
        "Content-Type": "application/json",
        "ai-sentry-consumer": "locustloadtest",
        "ai-sentry-log-level": "PII_STRIPPING_ENABLED",
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
                "content": "What does Microsoft do, and what is its most profitiable business division?"
            }
        ],
        "stream": True,
        "max_tokens": 800,
        "temperature": 0.7,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "top_p": 0.95,
        "stop": None
    }

    @task
    def post_openai(self):
        self.client.post(f"/openai/deployments/{aoai_deployment_name}/chat/completions?api-version=2024-02-15-preview", data=json.dumps(self.body), headers=self.headers)