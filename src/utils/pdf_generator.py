from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from typing import Dict, List
import datetime

class ExecutiveSummaryGenerator:
    def __init__(self, output_path: str = '/tmp/executive_summary.pdf'):
        self.output_path = output_path
        self.styles = getSampleStyleSheet()
        
        # Add custom styles
        self.styles.add(ParagraphStyle(name='TitleStyle', fontSize=18, spaceAfter=20, fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(name='HeadingStyle', fontSize=14, spaceAfter=10, fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(name='NormalStyle', fontSize=10, spaceAfter=6))
        
    def generate_report(self, compliance_score: int, finding_summary: Dict[str, int], critical_findings: List[str]):
        """
        Generates a 1-page executive summary PDF.
        """
        doc = SimpleDocTemplate(self.output_path, pagesize=letter)
        elements = []
        
        # 1. Title
        title = Paragraph(f"Cloud Data Governance Executive Summary", self.styles['TitleStyle'])
        elements.append(title)
        
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        elements.append(Paragraph(f"Generated on: {date_str}", self.styles['NormalStyle']))
        elements.append(Spacer(1, 20))
        
        # 2. Overall Compliance Score
        score_color = colors.green if compliance_score >= 80 else (colors.orange if compliance_score >= 60 else colors.red)
        score_text = f"<font color='{score_color.hexval()}'>{compliance_score}/100</font>"
        
        elements.append(Paragraph("Overall Compliance Score", self.styles['HeadingStyle']))
        elements.append(Paragraph(f"<b>Score:</b> {score_text}", self.styles['NormalStyle']))
        if compliance_score < 80:
            elements.append(Paragraph("Action Required: Your environment is below the target compliance threshold of 80.", self.styles['NormalStyle']))
        elements.append(Spacer(1, 20))
        
        # 3. Finding Breakdown Table
        elements.append(Paragraph("Finding Breakdown by Severity", self.styles['HeadingStyle']))
        
        data = [['Severity', 'Count']]
        for severity, count in finding_summary.items():
            data.append([severity, str(count)])
            
        table = Table(data, colWidths=[200, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # 4. Critical Findings / Top Recommendations
        elements.append(Paragraph("Top Critical Findings & Recommendations", self.styles['HeadingStyle']))
        
        if not critical_findings:
            elements.append(Paragraph("No critical findings detected. Excellent job!", self.styles['NormalStyle']))
        else:
            for i, finding in enumerate(critical_findings, 1):
                elements.append(Paragraph(f"{i}. {finding}", self.styles['NormalStyle']))
        
        # Generate PDF
        doc.build(elements)
        print(f"Executive Summary PDF generated at {self.output_path}")
        return self.output_path
