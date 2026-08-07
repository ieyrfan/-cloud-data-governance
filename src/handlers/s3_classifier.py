import json
import boto3
import os
import urllib.parse
from src.classifiers.pattern_matcher import find_sensitive_patterns, redact_sensitive_data
from src.classifiers.comprehend_client import ComprehendClient
from src.classifiers.confidence_scorer import calculate_confidence_score, determine_sensitivity_level
from src.utils.dynamodb_client import DynamoDBClient

# Initialize clients outside the handler for connection reuse
s3 = boto3.client('s3', endpoint_url=os.environ.get('LOCALSTACK_ENDPOINT'))
comprehend_client = ComprehendClient()
dynamodb_client = DynamoDBClient(table_name=os.environ.get('DYNAMODB_TABLE', 'DataGovernanceResults'))

# Context keywords that indicate sensitive data
CONTEXT_KEYWORDS = ['nric', 'salary', 'medical', 'confidential', 'password', 'credit', 'card', 'ic number']

def lambda_handler(event, context):
    """
    Triggered by S3 object creation.
    Downloads the file, classifies it, and stores the result in DynamoDB.
    """
    print("Received event:", json.dumps(event))
    
    # Handle S3 Event (usually wrapped in EventBridge or direct S3 trigger)
    # This assumes standard S3 event structure
    records = event.get('Records', [])
    
    for record in records:
        if 's3' not in record:
            continue
            
        bucket_name = record['s3']['bucket']['name']
        object_key = urllib.parse.unquote_plus(record['s3']['object']['key'])
        
        s3_uri = f"s3://{bucket_name}/{object_key}"
        print(f"Processing object: {s3_uri}")
        
        try:
            # 1. Fetch Data
            response = s3.get_object(Bucket=bucket_name, Key=object_key)
            file_bytes = response['Body'].read()
            
            # Use intelligent document parser
            from src.utils.document_parser import extract_text_from_file
            file_content = extract_text_from_file(file_bytes, object_key)
            
            if not file_content.strip():
                print(f"Skipping {s3_uri}: No extractable text found.")
                continue
            
            # 2. Layer 1: Pattern Matching
            pattern_matches = find_sensitive_patterns(file_content)
            
            # 3. Layer 2: Context Keyword Detection
            file_content_lower = file_content.lower()
            context_keywords_found = any(keyword in file_content_lower for keyword in CONTEXT_KEYWORDS)
            
            # 4. Layer 3: NLP with Comprehend
            comprehend_matches = comprehend_client.detect_pii(file_content)
            
            # 5. Confidence Scoring & Sensitivity
            confidence = calculate_confidence_score(pattern_matches, comprehend_matches, context_keywords_found)
            sensitivity = determine_sensitivity_level(pattern_matches, comprehend_matches)
            
            # Prepare findings payload
            findings = {
                'pattern_matches_count': sum(len(m) for m in pattern_matches.values()),
                'context_keywords_detected': context_keywords_found,
                'comprehend_entities_count': len(comprehend_matches)
            }
            
            print(f"Result for {s3_uri}: {sensitivity} (Confidence: {confidence})")
            
            # 6. Action: Data Redaction (Enterprise Feature)
            # If sensitive data is found, create a masked version in the clean bucket
            if sensitivity != 'PUBLIC':
                clean_bucket = os.environ.get('CLEAN_BUCKET', f"{bucket_name}-clean")
                try:
                    redacted_content = redact_sensitive_data(file_content, pattern_matches)
                    s3.put_object(
                        Bucket=clean_bucket,
                        Key=object_key,
                        Body=redacted_content.encode('utf-8'),
                        ContentType='text/plain',
                        Tagging='Status=REDACTED'
                    )
                    print(f"Successfully created redacted version in {clean_bucket}/{object_key}")
                except Exception as e:
                    print(f"Failed to save redacted version: {e}")
            
            # 7. Store Results
            dynamodb_client.save_classification_result(s3_uri, sensitivity, confidence, findings)
            
        except Exception as e:
            print(f"Error processing {s3_uri}: {str(e)}")
            continue

    return {
        'statusCode': 200,
        'body': json.dumps('Classification completed successfully.')
    }
