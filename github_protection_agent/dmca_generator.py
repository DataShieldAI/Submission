"""
DMCA Generator Module
Generates DMCA takedown notices with C2PA metadata support
"""
import os
from datetime import datetime
from typing import Dict
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import red, black, blue
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from dotenv import load_dotenv
load_dotenv()

from .utils import setup_logging

logger = setup_logging(__name__)


class DMCAGenerator:
    """Handles DMCA takedown notice generation"""
    
    def generate_dmca_pdf(self, dmca_data: Dict) -> str:
        """Generate DMCA takedown notice PDF"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"dmca_notice_{dmca_data['original_repo']['id']}_{timestamp}.pdf"
            
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Custom styles
            title_style = ParagraphStyle(
                'DMCATitle',
                parent=styles['Title'],
                fontSize=16,
                textColor=red,
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'DMCAHeading',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=black,
                spaceAfter=12,
                spaceBefore=12
            )
            
            body_style = ParagraphStyle(
                'DMCABody',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_JUSTIFY,
                spaceAfter=12
            )
            
            # Title
            story.append(Paragraph(
                "Digital Millennium Copyright Act (DMCA) Takedown Notice",
                title_style
            ))
            
            # Date and From
            story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", body_style))
            story.append(Paragraph("From: Kreon Labs IP Protection Unit", body_style))
            story.append(Paragraph("Email: legal@kreonlabs.com", body_style))
            story.append(Spacer(1, 20))
            
            # To Section
            story.append(Paragraph("To: GitHub, Inc.", body_style))
            story.append(Paragraph("88 Colin P Kelly Jr St", body_style))
            story.append(Paragraph("San Francisco, CA 94107", body_style))
            story.append(Paragraph("Via: copyright@github.com", body_style))
            story.append(Spacer(1, 20))
            
            # Introduction
            story.append(Paragraph("To Whom It May Concern:", body_style))
            story.append(Spacer(1, 12))
            
            intro_text = """This is a formal notification under Section 512(c) of the Digital Millennium Copyright Act 
            (DMCA) seeking the removal of infringing material from your service. I certify under penalty of perjury 
            that I am authorized to act on behalf of the owner of the intellectual property rights described below."""
            story.append(Paragraph(intro_text, body_style))
            story.append(Spacer(1, 20))
            
            # 1. Copyrighted Work
            story.append(Paragraph("1. IDENTIFICATION OF COPYRIGHTED WORK", heading_style))
            
            original_repo = dmca_data['original_repo']
            work_data = [
                ['Repository URL:', original_repo['github_url']],
                ['Repository ID:', str(original_repo['id'])],
                ['Registration Date:', original_repo['registered_at']],
                ['Blockchain TX:', original_repo['tx_hash'][:16] + '...'],
                ['Content Hash:', original_repo['repo_hash'][:32] + '...'],
                ['License Type:', original_repo['license_type']]
            ]
            
            work_table = Table(work_data, colWidths=[2*inch, 4*inch])
            work_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(work_table)
            story.append(Spacer(1, 20))
            
            # 2. Infringing Material
            story.append(Paragraph("2. IDENTIFICATION OF INFRINGING MATERIAL", heading_style))
            
            infringing_repo = dmca_data['infringing_repo']
            infringing_data = [
                ['Infringing URL:', infringing_repo['url']],
                ['Repository Name:', infringing_repo.get('name', 'Unknown')],
                ['Similarity Score:', f"{dmca_data['similarity_score']:.2%}"],
                ['Detection Date:', dmca_data['timestamp']]
            ]
            
            infringing_table = Table(infringing_data, colWidths=[2*inch, 4*inch])
            infringing_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(infringing_table)
            story.append(Spacer(1, 20))
            
            # 3. Evidence of Infringement
            story.append(Paragraph("3. EVIDENCE OF INFRINGEMENT", heading_style))
            
            evidence_text = f"""Our automated analysis has detected substantial similarity between the protected 
            repository and the allegedly infringing material. The similarity score of {dmca_data['similarity_score']:.2%} 
            indicates significant code duplication beyond what would be expected from coincidental development."""
            story.append(Paragraph(evidence_text, body_style))
            
            if dmca_data.get('evidence'):
                story.append(Paragraph("Specific evidence includes:", body_style))
                for evidence_item in dmca_data['evidence'][:5]:  # Limit to 5 items
                    story.append(Paragraph(f"• {evidence_item}", body_style))
            
            story.append(Spacer(1, 20))
            
            # 4. C2PA Verification
            story.append(Paragraph("4. CONTENT AUTHENTICITY & PROVENANCE", heading_style))
            
            c2pa_text = """The original work is protected with C2PA (Coalition for Content Provenance and Authenticity) 
            metadata, providing cryptographic proof of ownership and creation date. This metadata has been verified and 
            is stored on the blockchain for immutable reference."""
            story.append(Paragraph(c2pa_text, body_style))
            story.append(Spacer(1, 20))
            
            # 5. Statement of Good Faith
            story.append(Paragraph("5. STATEMENT OF GOOD FAITH", heading_style))
            
            good_faith_text = """I have a good faith belief that use of the material in the manner complained of is 
            not authorized by the copyright owner, its agent, or the law."""
            story.append(Paragraph(good_faith_text, body_style))
            story.append(Spacer(1, 20))
            
            # 6. Statement of Accuracy
            story.append(Paragraph("6. STATEMENT OF ACCURACY", heading_style))
            
            accuracy_text = """I certify under penalty of perjury that the information in this notification is 
            accurate and that I am authorized to act on behalf of the owner of an exclusive right that is 
            allegedly infringed."""
            story.append(Paragraph(accuracy_text, body_style))
            story.append(Spacer(1, 20))
            
            # 7. Requested Action
            story.append(Paragraph("7. REQUESTED ACTION", heading_style))
            
            action_text = """Please expeditiously remove or disable access to the infringing material. 
            Please also provide written confirmation when this has been completed."""
            story.append(Paragraph(action_text, body_style))
            story.append(Spacer(1, 30))
            
            # Signature
            story.append(Paragraph("Sincerely,", body_style))
            story.append(Spacer(1, 30))
            story.append(Paragraph("_______________________", body_style))
            story.append(Paragraph("Kreon Labs IP Protection Unit", body_style))
            story.append(Paragraph("Authorized Agent", body_style))
            story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", body_style))
            
            # Footer with reference numbers
            story.append(Spacer(1, 30))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=blue
            )
            story.append(Paragraph(f"Reference: DMCA-{dmca_data['original_repo']['id']}-{timestamp}", footer_style))
            story.append(Paragraph(f"Original Repository Hash: {original_repo['repo_hash']}", footer_style))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"📄 DMCA notice generated: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error generating DMCA PDF: {e}")
            raise
    
    def generate_c2pa_dmca_notice(self, dmca_data: Dict, c2pa_metadata: Dict) -> str:
        """Generate DMCA notice with embedded C2PA metadata"""
        # This would integrate with the C2PA tools to embed metadata
        # For now, we generate a standard PDF
        pdf_path = self.generate_dmca_pdf(dmca_data)
        
        # TODO: Integrate with C2PA tools to embed metadata
        # c2pa_result = writeC2PA(pdf_path, 'application/pdf', ...)
        
        return pdf_path