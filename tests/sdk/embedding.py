import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv(".env", override=True)

client = AzureOpenAI(
  api_key = os.getenv("api_key"),  
  api_version = "2024-02-01",
  azure_endpoint = os.getenv("azure_endpoint", "http://localhost:6124/"), 
)

response = client.embeddings.create(
    input = "Your text string goes here",
    model= "text-embedding-ada-002"
)

print(response.model_dump_json(indent=2))