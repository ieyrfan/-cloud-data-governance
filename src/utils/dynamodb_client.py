import boto3
import os
import uuid
from datetime import datetime

class DynamoDBClient:
    def __init__(self, table_name: str, region_name='us-east-1'):
        self.table_name = table_name
        
        endpoint_url = os.environ.get('LOCALSTACK_ENDPOINT')
        if endpoint_url:
            self.dynamodb = boto3.resource('dynamodb', region_name=region_name, endpoint_url=endpoint_url)
        else:
            self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
            
        self.table = self.dynamodb.Table(self.table_name)

    def save_classification_result(self, s3_uri: str, sensitivity: str, confidence: float, findings: dict):
        """
        Saves the classification result to DynamoDB.
        """
        item = {
            'resource_id': s3_uri,
            'version_id': str(uuid.uuid4()),
            'sensitivity_level': sensitivity,
            'confidence_score': str(round(confidence, 2)), # DynamoDB floats must be string or Decimal
            'findings': findings,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            self.table.put_item(Item=item)
            return True
        except Exception as e:
            print(f"Error saving to DynamoDB: {e}")
            return False
