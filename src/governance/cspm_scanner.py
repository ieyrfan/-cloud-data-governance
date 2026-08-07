import boto3
import os

class CSPMScanner:
    """
    Cloud Security Posture Management (CSPM) Scanner.
    Similar to AWS Security Hub or Palo Alto Prisma Cloud.
    Continuously audits the cloud environment for misconfigurations.
    """
    def __init__(self, region_name='us-east-1'):
        self.s3 = boto3.client('s3', region_name=region_name, endpoint_url=os.environ.get('LOCALSTACK_ENDPOINT'))
        self.iam = boto3.client('iam', region_name=region_name, endpoint_url=os.environ.get('LOCALSTACK_ENDPOINT'))
        
    def scan_s3_posture(self):
        """
        Scans all S3 buckets for missing security controls (Encryption, Versioning, Public Access Block).
        """
        print("🔍 [CSPM] Scanning S3 Data Lakes for misconfigurations...")
        findings = []
        try:
            response = self.s3.list_buckets()
            for bucket in response.get('Buckets', []):
                bucket_name = bucket['Name']
                
                # Check Versioning (Protection against Ransomware/Accidental Deletion)
                try:
                    vers = self.s3.get_bucket_versioning(Bucket=bucket_name)
                    if vers.get('Status') != 'Enabled':
                        findings.append(f"Bucket {bucket_name} lacks Versioning (Ransomware Risk)")
                except Exception:
                    findings.append(f"Bucket {bucket_name} Versioning could not be verified")
                    
                # Check Public Access Block
                try:
                    pab = self.s3.get_public_access_block(Bucket=bucket_name)
                    conf = pab.get('PublicAccessBlockConfiguration', {})
                    if not all([conf.get('BlockPublicAcls'), conf.get('IgnorePublicAcls'), conf.get('BlockPublicPolicy'), conf.get('RestrictPublicBuckets')]):
                        findings.append(f"Bucket {bucket_name} has incomplete Public Access Block")
                except Exception:
                    findings.append(f"Bucket {bucket_name} has NO Public Access Block configured! (CRITICAL)")
                    
            return findings
        except Exception as e:
            print(f"CSPM Scan failed: {e}")
            return []
