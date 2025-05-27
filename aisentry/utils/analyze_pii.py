import asyncio
import logging
import os
import json
from typing import List
from dotenv import load_dotenv

from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics.aio import TextAnalyticsClient
from azure.ai.textanalytics import RecognizePiiEntitiesAction
import re

async def analyze_pii_async(input_text: List[str]) -> List[str]:
    """
    Processes a list of JSON strings, redacts PII, and returns valid JSON strings.
    """
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=getattr(logging, log_level),
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%d-%m-%Y %H:%M:%S'
                        )
    load_dotenv(".env", override=True)
    logger.debug(f"input_text: {input_text}")

    chunk_size = 1250
    endpoint = os.environ["AI-SENTRY-LANGUAGE-ENDPOINT"]
    key = os.environ["AI-SENTRY-LANGUAGE-KEY"]
    logger.info(f"Using cognitive endpoint: {endpoint}")

    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )



def smart_json_loads(s: str):
    """
    Attempts to load a JSON string, unescaping double backslashes if necessary.
    """
    try:
        # Try normal loading first
        return json.loads(s)
    except json.JSONDecodeError:
        # Heuristic: if there are many double backslashes, try unescaping
        if re.search(r'\\\\', s):
            try:
                unescaped = s.encode().decode('unicode_escape')
                return json.loads(unescaped)
            except Exception:
                pass
        raise  # Re-raise if still failing

    async def redact_pii_in_obj(obj, pii_entities):
        """
        Recursively redacts PII entities in a JSON-like Python object.
        """
        if isinstance(obj, dict):
            return {k: await redact_pii_in_obj(v, pii_entities) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [await redact_pii_in_obj(item, pii_entities) for item in obj]
        elif isinstance(obj, str):
            redacted = obj
            for ent in pii_entities:
                if ent["confidence_score"] >= 0.8 and ent["category"] != "DateTime":
                    redacted = redacted.replace(ent["text"], "PII_REDACTED")
            return redacted
        else:
            return obj

    output_texts = []

    for i in range(0, len(input_text), chunk_size):
        chunk = input_text[i:i+chunk_size]
        logger.info(f"Processing chunk of size {len(chunk)}")

        async with text_analytics_client:
            poller = await text_analytics_client.begin_analyze_actions(
                chunk,
                display_name="PII Analysis",
                actions=[RecognizePiiEntitiesAction()]
            )
            pages = await poller.result()
            document_results = []
            async for page in pages:
                document_results.append(page)

        # For each document, parse as JSON, redact PII, then dump as JSON string
        for doc_str, action_results in zip(chunk, document_results):
            pii_entities = []
            for result in action_results:
                if result.kind == "PiiEntityRecognition" and not result.is_error:
                    for entity in result.entities:
                        logger.debug(f"......Entity: {entity.text}")
                        logger.debug(f".........Category: {entity.category}")
                        logger.debug(f".........Confidence Score: {entity.confidence_score}")
                        pii_entities.append({
                            "text": entity.text,
                            "category": entity.category,
                            "confidence_score": entity.confidence_score
                        })
                elif getattr(result, "is_error", False):
                    logger.error(f'PII-Processing: An error with code {result.error.code} and message {result.error.message}')
            try:
                #data = json.loads(doc_str)
                data = smart_json_loads(doc_str)
                redacted_data = await redact_pii_in_obj(data, pii_entities)
                redacted_json = json.dumps(redacted_data, ensure_ascii=False, separators=(',', ':'))
                output_texts.append(redacted_json)
            except Exception as e:
                logger.error(f"Error redacting or serializing JSON: {e}")
                # Optionally, append the unredacted doc or an empty string
                output_texts.append(doc_str)

    logger.info(f"PII stripping completed")
    return output_texts