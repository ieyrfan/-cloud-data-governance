from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import boto3
import os
from typing import Dict, List

app = FastAPI(
    title="Data Governance API",
    description="Enterprise API for querying Data Risk Scores and Compliance Mappings",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=os.environ.get('LOCALSTACK_ENDPOINT'),
    region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
)
TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'data-governance-results-dev')

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "data-governance-api"}

@app.get("/dashboard/summary")
def get_dashboard_summary():
    """
    Returns aggregated metrics for the executive dashboard.
    """
    try:
        table = dynamodb.Table(TABLE_NAME)
        response = table.scan()
        items = response.get('Items', [])
        
        summary = {
            "total_files_scanned": len(items),
            "sensitivity_breakdown": {
                "RESTRICTED": 0,
                "CONFIDENTIAL": 0,
                "INTERNAL": 0,
                "PUBLIC": 0
            },
            "high_risk_files": 0
        }
        
        for item in items:
            sens = item.get('sensitivity_level', 'PUBLIC')
            if sens in summary["sensitivity_breakdown"]:
                summary["sensitivity_breakdown"][sens] += 1
            
            # Simulated risk calculation lookup
            if sens in ['RESTRICTED', 'CONFIDENTIAL']:
                summary["high_risk_files"] += 1
                
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/{file_id:path}/risk")
def get_file_risk_score(file_id: str):
    """
    Queries DynamoDB to return the specific compliance findings and risk level for a file.
    Example file_id: s3://data-lake-governance-dev/document.pdf
    """
    try:
        table = dynamodb.Table(TABLE_NAME)
        response = table.get_item(Key={'resource_id': file_id, 'version_id': 'latest'})
        item = response.get('Item')
        
        if not item:
            raise HTTPException(status_code=404, detail="File classification not found.")
            
        return {
            "resource_id": item['resource_id'],
            "sensitivity": item.get('sensitivity_level'),
            "confidence_score": item.get('confidence_score'),
            "findings": item.get('findings', []),
            "compliance_status": "NON_COMPLIANT" if item.get('sensitivity_level') in ['RESTRICTED', 'CONFIDENTIAL'] else "COMPLIANT"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mangum wrapper for AWS Lambda deployment
handler = Mangum(app)
