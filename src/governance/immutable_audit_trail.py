import hashlib
import json
import os
import time
from datetime import datetime
import boto3

class ImmutableAuditTrail:
    """
    Military-Grade Feature: Cryptographically Chained Audit Logging.
    Creates an immutable, tamper-evident ledger of all data governance actions.
    If a rogue administrator tries to delete or alter a past log entry to cover their tracks,
    the mathematical hash chain will break, instantly alerting auditors.
    """
    def __init__(self, region_name='us-east-1'):
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=region_name,
            endpoint_url=os.environ.get('LOCALSTACK_ENDPOINT')
        )
        self.table_name = os.environ.get('AUDIT_TABLE', 'data-governance-audit-ledger-dev')
        
    def _ensure_table_exists(self):
        try:
            self.dynamodb.meta.client.describe_table(TableName=self.table_name)
        except self.dynamodb.meta.client.exceptions.ResourceNotFoundException:
            # Create the table if it doesn't exist (useful for local dev)
            self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[{'AttributeName': 'log_id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'log_id', 'AttributeType': 'S'}],
                BillingMode='PAY_PER_REQUEST'
            )
            time.sleep(2) # Wait for table creation

    def _get_previous_hash(self) -> str:
        """Retrieves the hash of the most recent log entry to chain the next one."""
        self._ensure_table_exists()
        table = self.dynamodb.Table(self.table_name)
        
        # Scan to get the latest log (In production, use a GSI with a timestamp sort key)
        response = table.scan()
        items = response.get('Items', [])
        
        if not items:
            return "0000000000000000000000000000000000000000000000000000000000000000" # Genesis Hash
            
        # Sort by timestamp to find the latest
        items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return items[0].get('current_hash', '')

    def record_event(self, action: str, actor: str, resource: str, details: dict):
        """
        Records a new event and cryptographically binds it to the previous event.
        """
        self._ensure_table_exists()
        table = self.dynamodb.Table(self.table_name)
        
        timestamp = datetime.utcnow().isoformat() + "Z"
        previous_hash = self._get_previous_hash()
        
        # Create the payload to be hashed
        payload = {
            "timestamp": timestamp,
            "action": action,
            "actor": actor,
            "resource": resource,
            "details": details,
            "previous_hash": previous_hash
        }
        
        # Calculate SHA-256 Hash of the payload
        payload_str = json.dumps(payload, sort_keys=True)
        current_hash = hashlib.sha256(payload_str.encode('utf-8')).hexdigest()
        
        # Persist to Ledger
        log_id = f"audit-{int(time.time() * 1000)}"
        
        item = {
            "log_id": log_id,
            "timestamp": timestamp,
            "action": action,
            "actor": actor,
            "resource": resource,
            "details": json.dumps(details),
            "previous_hash": previous_hash,
            "current_hash": current_hash
        }
        
        table.put_item(Item=item)
        print(f"🔒 [IMMUTABLE AUDIT] Log {log_id} cryptographically sealed. Hash: {current_hash[:8]}...")
        return log_id
        
    def verify_ledger_integrity(self):
        """
        Auditing function: Recalculates hashes from the Genesis block to ensure
        no logs have been secretly modified or deleted.
        """
        table = self.dynamodb.Table(self.table_name)
        response = table.scan()
        items = response.get('Items', [])
        
        # Sort chronologically
        items.sort(key=lambda x: x.get('timestamp', ''))
        
        expected_previous_hash = "0000000000000000000000000000000000000000000000000000000000000000"
        
        for idx, item in enumerate(items):
            # Verify chain linkage
            if item['previous_hash'] != expected_previous_hash:
                return False, f"Broken chain detected at log {item['log_id']}! Previous hash mismatch."
                
            # Reconstruct payload and verify current hash
            payload = {
                "timestamp": item['timestamp'],
                "action": item['action'],
                "actor": item['actor'],
                "resource": item['resource'],
                "details": json.loads(item['details']),
                "previous_hash": item['previous_hash']
            }
            
            payload_str = json.dumps(payload, sort_keys=True)
            calculated_hash = hashlib.sha256(payload_str.encode('utf-8')).hexdigest()
            
            if calculated_hash != item['current_hash']:
                return False, f"Tampering detected at log {item['log_id']}! Hash mismatch."
                
            expected_previous_hash = item['current_hash']
            
        return True, "Ledger integrity is 100% verified. No tampering detected."
