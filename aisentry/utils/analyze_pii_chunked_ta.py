import asyncio
import logging
from typing import List


batch_size = 1250 # Azure has a limit of 1250 characters per document
def chunk_string(string, chunk_size):
    return [string[i:i+chunk_size] for i in range(0, len(string), chunk_size)]


#def chunk_reponse_body(response_body: str) -> List[str]:
    


async def analyze_pii_async(input_text: str) -> None:
    # [START analyze_async]
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics.aio import TextAnalyticsClient
    from azure.ai.textanalytics import (
        RecognizeEntitiesAction,
        RecognizeLinkedEntitiesAction,
        RecognizePiiEntitiesAction,
        ExtractKeyPhrasesAction,
        AnalyzeSentimentAction,
    )

    endpoint = os.environ["AI-SENTRY-LANGUAGE-ENDPOINT"]
    key = os.environ["AI-SENTRY-LANGUAGE-KEY"]
    print(f"inputData: {input_text}")

    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )


    for doc in input_text:
        logging.info(f"CHUNKING DOC: {doc}")
        chunks = chunk_string(doc, batch_size)  
        for chunk in chunks:
            actions = [RecognizePiiEntitiesAction()]
            poller = await text_analytics_client.begin_analyze_actions([chunk], actions, language="en")
            result = await poller.result()

            async for doc in result:
                print("Redacted Text: {}".format(doc.redacted_text))
                async for entity in doc.entities:
                    print("Entity: {}".format(entity.text))
                    print("Category: {}".format(entity.category))
                    print("Confidence Score: {}\n".format(entity.confidence_score))


