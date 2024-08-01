import os
import logging
import asyncio
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI



# initial setup for logging / env variable loading
log_level = os.getenv('LOG-LEVEL', 'INFO').upper()

# Set up the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=getattr(logging, log_level),
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S'
                    )

# Initialize the OpenAI client with your key and endpoint

load_dotenv(".env", override=True)

openai_key = os.environ.get("PII_STRIPPING_OPENAI_API_KEY")
openai_endpoint = os.environ.get("PII_STRIPPING_OPENAI_ENDPOINT")


client = AsyncAzureOpenAI(
    api_key=openai_key,  
    api_version="2023-12-01-preview",
    azure_endpoint=openai_endpoint
)

pii_stripping_system_prompt = """Objective: Identify and flag any Personally Identifiable Information (PII) within text data to ensure data privacy and compliance with regulations such as GDPR, CCPA, etc.

PII includes but is not limited to:
Full Names: First and last names
Addresses: Street address, city, state, zip code
Phone Numbers: Any format of telephone numbers
Email Addresses: Any format of email addresses
Social Security Numbers (SSNs): XXX-XX-XXXX or similar formats
Credit Card Numbers: Any format of credit/debit card numbers
Bank Account Numbers: Any format of bank account numbers
Driver's License Numbers: Any format of driver's license numbers
Passport Numbers: Any format of passport numbers
Date of Birth: Full date of birth (MM/DD/YYYY or similar formats)
IP Addresses: Any format of IPv4 or IPv6 addresses
API-KEY or Token: Any format of API keys or tokens
Medical Information: Any health-related information that can identify an individual
Biometric Data: Fingerprints, facial recognition data, etc.

Instructions for the System:
Input: Accept text data for analysis.
Processing:
Use pattern matching, regular expressions, and machine learning algorithms to identify potential PII.
Cross-reference detected patterns with known PII formats.
Output:
Flag detected PII and categorize it.
Provide a confidence score for each detected PII item.
Highlight the specific text containing PII.

Example:

Input Text:

John Doe lives at 123 Maple Street, Springfield, IL 62704. His email is john.doe@example.com, and his phone number is (555) 123-4567. He was born on 01/15/1985 and his SSN is 123-45-6789.  
 
Output:

Keep the same text structure but replace the PII with placeholders: [PII-Redacted]
 
Compliance Note: The system must handle all detected PII with strict confidentiality and in accordance with applicable data protection regulations."""


async def get_chat_pii_stripped_completion(prompt):
    # Send the request to Azure OpenAI
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
    {"role": "system", "content": pii_stripping_system_prompt},
    {"role": "user", "content": f"Rewrite the input and Strip out PII information as per the system message from following input: {prompt}"}
  ]
    )

    # Extract the text from the response
    #completion_text = response.completions[0].data.get("text", "")
    message_content = response['choices'][0]['message']['content']

    logger.info(f"PII Stripped Completion Text: {message_content}")
    return message_content


