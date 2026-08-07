import boto3
import os
from typing import List, Dict, Any

class ComprehendClient:
    def __init__(self, region_name='us-east-1'):
        # In LocalStack, endpoint_url must be provided.
        # In AWS, it uses the default endpoint.
        endpoint_url = os.environ.get('LOCALSTACK_ENDPOINT')
        if endpoint_url:
            self.client = boto3.client('comprehend', region_name=region_name, endpoint_url=endpoint_url)
        else:
            self.client = boto3.client('comprehend', region_name=region_name)

    def detect_pii(self, text: str, language_code: str = 'en') -> List[Dict[str, Any]]:
        """
        Uses Amazon Comprehend to detect PII entities in unstructured text.
        """
        if not text:
            return []
            
        try:
            # Comprehend has a 100KB limit per request. 
            # For simplicity in this example, we'll truncate or assume text is within limits.
            # In production, chunking logic is required.
            truncated_text = text[:99000]
            
            response = self.client.detect_pii_entities(
                Text=truncated_text,
                LanguageCode=language_code
            )
            return response.get('PiiEntities', [])
        except Exception as e:
            print(f"Error calling Comprehend: {e}")
            return []
