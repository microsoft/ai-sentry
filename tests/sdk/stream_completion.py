
import os
import asyncio
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv
from timeit import default_timer

load_dotenv(".env", override=True)

azure_openai_client = AsyncAzureOpenAI(
  azure_endpoint = os.getenv("azure_endpoint", "http://localhost:6124/"), 
  api_key=os.getenv("api_key", "yourapikey"),  
  api_version=os.getenv("api_version", "2023-07-01-preview")
)


async def get_response(message):
    start = default_timer()
    end_first_chunk = None
    end = None
    response = await azure_openai_client.chat.completions.create(
        model = os.getenv("aoai_deployment", "chat"),
        temperature = 0.4,
        messages = [
            {"role": "user", "content": message}
        ],
        stream=True
    )
    #print(response.model_dump_json(indent=2)) - > not response

    async for chunk in response:
        if not end_first_chunk:
            end_first_chunk = default_timer()
        print(chunk .model_dump_json(indent=2))

    end = default_timer()

    print(f"Elapse: {end-start}, First Chunk: {end_first_chunk-start}, Last Chunk: {end-end_first_chunk}")

def main():
    print("Azure OpenAI SDK Stream Completion Test")
    asyncio.run(get_response('What does Microsoft do?'))


if __name__ == "__main__":
    main()