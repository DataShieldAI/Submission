"""
Report Generator Module
Handles PDF report generation for security audits
"""
from datetime import datetime
from typing import Dict

from .utils import setup_logging

logger = setup_logging(__name__)

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import red, black, green
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning("⚠️ ReportLab not installed. PDF generation will be disabled.")


class ReportGenerator:
    """Handles report generation"""
    
    def generate_security_pdf(self, audit_result: Dict) -> str:
        """Generate PDF security report"""
        
        if not PDF_AVAILABLE:
            logger.warning("⚠️ PDF generation not available (ReportLab not installed)")
            return None
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"security_audit_{audit_result['audit_id']}_{timestamp}.pdf"
            
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                textColor=red
            )
            story.append(Paragraph("🚨 SECURITY AUDIT REPORT", title_style))
            story.append(Spacer(1, 12))
            
            # Basic info
            info_data = [
                ['Audit ID:', str(audit_result['audit_id'])],
                ['Timestamp:', audit_result['timestamp']],
                ['Target URL:', audit_result['input_url']],
                ['Platform:', audit_result['platform']],
                ['Files Scanned:', str(audit_result['files_scanned'])],
                ['Total Findings:', str(audit_result['total_findings'])]
            ]
            
            info_table = Table(info_data, colWidths=[2*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), green),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, black)
            ]))
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # Findings summary
            story.append(Paragraph("📊 FINDINGS SUMMARY", styles['Heading2']))
            summary_data = [
                ['Severity', 'Count'],
                ['Critical', str(audit_result['critical_findings'])],
                ['High', str(audit_result['high_findings'])],
                ['Medium', str(audit_result['medium_findings'])],
                ['Low', str(audit_result['low_findings'])]
            ]
            
            summary_table = Table(summary_data, colWidths=[3*inch, 1*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), green),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, black)
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Detailed findings
            if audit_result['findings']:
                story.append(Paragraph("🔍 DETAILED FINDINGS", styles['Heading2']))
                
                for i, finding in enumerate(audit_result['findings'][:10], 1):  # Limit to first 10
                    story.append(Paragraph(
                        f"Finding #{i}: {finding.get('pattern_name', finding.get('type', 'Unknown'))}", 
                        styles['Heading3']
                    ))
                    
                    finding_details = [
                        ['Severity:', finding.get('severity', 'Unknown')],
                        ['Description:', finding.get('description', 'N/A')],
                        ['File:', finding.get('file_path', 'N/A')],
                        ['Recommendation:', finding.get('recommendation', 'Review and remediate')]
                    ]
                    
                    finding_table = Table(finding_details, colWidths=[1.5*inch, 4.5*inch])
                    finding_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('GRID', (0, 0), (-1, -1), 1, black)
                    ]))
                    story.append(finding_table)
                    story.append(Spacer(1, 15))
            
            # AI Summary
            if audit_result.get('ai_summary'):
                story.append(Paragraph("🤖 AI ANALYSIS", styles['Heading2']))
                story.append(Paragraph(audit_result['ai_summary'], styles['Normal']))
            
            doc.build(story)
            logger.info(f"📄 Security audit PDF report generated: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error generating PDF report: {e}")
            return None
    
    def generate_violation_report(self, violations: List[Dict]) -> str:
        """Generate violation report"""
        
        if not PDF_AVAILABLE:
            return None
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"violation_report_{timestamp}.pdf"
            
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                textColor=red
            )
            story.append(Paragraph("⚠️ CODE VIOLATION REPORT", title_style))
            story.append(Spacer(1, 12))
            
            # Summary
            story.append(Paragraph(f"Total Violations Found: {len(violations)}", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            # Violations table
            if violations:
                violation_data = [['Repository', 'Similarity', 'Language', 'Created']]
                
                for v in violations:
                    violation_data.append([
                        v.get('name', 'Unknown'),
                        f"{v.get('similarity', 0):.2%}",
                        v.get('language', 'N/A'),
                        v.get('created_at', 'N/A')[:10]
                    ])
                
                violation_table = Table(violation_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1.5*inch])
                violation_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), red),
                    ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, black)
                ]))
                story.append(violation_table)
            
            doc.build(story)
            logger.info(f"📄 Violation report generated: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error generating violation report: {e}")
            return None