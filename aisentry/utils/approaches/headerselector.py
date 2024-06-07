from dataclasses import dataclass

@dataclass
class AzureOpenAIDeployment:
    url: str
    retry_ms: int
    ratelimit_remaining_tokens: int
    ratelimit_remaining_requests: int

class HeaderSelector:

    def __init__(
            self,
            openai_urls: [str]
    ):
        self.openai_urls = openai_urls

    def get_next_aoai(prompt: str):
        token_estimate = len(prompt)/4
