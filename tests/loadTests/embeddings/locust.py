from locust import HttpUser, task, between

class EmbeddingTestUser(HttpUser):
    wait_time = between(1, 5)  # Simulated users will wait 1-5 seconds between tasks
    
    @task
    def post_embedding(self):
        headers = {
            "Content-Type": "application/json",
            "api-key": "your_api_key_here",  # Replace with your actual API key
            "ai-sentry-backend-pool": "pool1",
            "ai-sentry-consumer": "embedding-automated-test1",
            "ai-sentry-log-level": "PII_STRIPPING_ENABLED",
            "ai-sentry-adapters": "[]"
        }
        payload = {
            "input": "Sample Document goes here"
        }
        self.client.post("/openai/deployments/text-embedding-ada-002/embeddings?api-version=2024-06-01", json=payload, headers=headers)

# Note: Ensure you replace "your_api_key_here" with the actual API key.
# You might also need to adjust the host in the Locust command-line or within the script if it's dynamic.