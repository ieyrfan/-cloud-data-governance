import os
import urllib.request
import urllib.parse
import json

class SecurityAlerter:
    """
    ChatOps Integration: Sends critical security alerts directly to the Security Team's Slack or Discord channel.
    Provides instant visibility without needing to refresh a dashboard.
    """
    def __init__(self):
        # In a real environment, this would be an AWS Secrets Manager lookup
        self.webhook_url = os.environ.get('SLACK_WEBHOOK_URL', '')
        
    def send_critical_alert(self, title: str, message: str, resource: str):
        print(f"📡 [CHAT-OPS] Preparing to send Critical Alert to Security Team...")
        
        payload = {
            "text": f"🚨 *CRITICAL SECURITY INCIDENT* 🚨\n*Type:* {title}\n*Resource:* `{resource}`\n*Details:* {message}"
        }
        
        # If no webhook is configured (like in our local test environment), just print it beautifully
        if not self.webhook_url:
            print(f"💬 [MOCK SLACK MESSAGE]\n{payload['text']}\n----------------------------------")
            return True
            
        try:
            req = urllib.request.Request(
                self.webhook_url, 
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req, timeout=5)
            print("✅ Alert successfully sent to Slack/Discord!")
            return True
        except Exception as e:
            print(f"Failed to send alert: {e}")
            return False
