import asyncio
import logging
from typing import List


async def analyze_pii_async(input_text: List[str]) -> None:
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


    # initial setup for logging / env variable loading
    log_level = os.getenv('LOG-LEVEL', 'INFO').upper()

    # Set up the logger
    logging.basicConfig(level=getattr(logging, log_level))
    logger = logging.getLogger(__name__)

    logger.debug(f"input_text: {input_text}")
    chunk_size = 1250
    doc=""

    endpoint = os.environ["AI-SENTRY-LANGUAGE-ENDPOINT"]
    key = os.environ["AI-SENTRY-LANGUAGE-KEY"]

    logging.info(f"Using cognitive endpoint: {endpoint}")


    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )
    for i in range(0, len(input_text), chunk_size):
        chunk = input_text[i:i+chunk_size]
        # Process the chunk
        print(f"Processing chunk {chunk}")

        async with text_analytics_client:
            poller = await text_analytics_client.begin_analyze_actions(
                chunk,
                display_name="PII Analysis",
                actions=[
                    RecognizePiiEntitiesAction()
                ]
            )

            pages = await poller.result()

            document_results = []
            async for page in pages:
                document_results.append(page)

        for doc, action_results in zip(chunk, document_results):
            for result in action_results:

                if result.kind == "PiiEntityRecognition":
                    print("...Results of Recognize PII Entities action:")
                    for pii_entity in result.entities:
                        logger.debug(f"......Entity: {pii_entity.text}")
                        logger.debug(f".........Category: {pii_entity.category}")
                        logger.debug(f".........Confidence Score: {pii_entity.confidence_score}")
                        if pii_entity.confidence_score >= 0.8 and pii_entity.category != "DateTime":
                            logger.debug(f"Removing PII entity: {pii_entity.text}, category: {pii_entity.category} from the logged payload")
                            doc = doc.replace(pii_entity.text, "PII_REDACTED")

                elif result.is_error is True:
                    logger.error(f'PII-Processing: An error with code {result.error.code} and message {result.error.message}')
    

    #UNTOCHED 
    if ": PII_REDACTED," in doc:
        doc = doc.replace(": PII_REDACTED,", ":\"PII_REDACTED\",")

    if "PII_REDACTED," in doc:
        doc = doc.replace("PII_REDACTED,", "PII_REDACTED\"")

    logger.info(f"PII stripping completed")
    return doc

