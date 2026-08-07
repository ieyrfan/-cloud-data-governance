from typing import Dict, Any

class RiskScoringEngine:
    def __init__(self):
        self.sensitivity_weights = {
            'RESTRICTED': 10,
            'CONFIDENTIAL': 5,
            'INTERNAL': 2,
            'PUBLIC': 1,
            'UNKNOWN': 0
        }
        
    def calculate_risk_score(self, sensitivity: str, exposure_level: int, access_breadth: int) -> int:
        """
        Calculates the risk score based on the formula:
        Risk Score = (Data Sensitivity Weight) × (Exposure Level) × (Access Breadth)
        
        exposure_level: e.g., 1=Private, 5=Internal Shared, 10=Public
        access_breadth: Number of distinct IAM roles/users with access.
        """
        weight = self.sensitivity_weights.get(sensitivity.upper(), 0)
        return weight * exposure_level * access_breadth
        
    def categorize_risk(self, risk_score: int) -> str:
        """
        Categorizes finding into severity levels based on score thresholds.
        """
        if risk_score >= 80:
            return 'CRITICAL'
        elif risk_score >= 40:
            return 'HIGH'
        elif risk_score >= 15:
            return 'MEDIUM'
        elif risk_score > 0:
            return 'LOW'
        else:
            return 'INFO'
