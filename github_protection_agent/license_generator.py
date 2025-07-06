"""
License Generator Module
Generates license PDFs for registered repositories
"""
import os
from datetime import datetime
from typing import Dict
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, blue
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from dotenv import load_dotenv
load_dotenv()

from .utils import setup_logging

logger = setup_logging(__name__)


class LicenseGenerator:
    """Handles license PDF generation"""
    
    def __init__(self):
        self.licenses = {
            'MIT': self._get_mit_license,
            'Apache-2.0': self._get_apache_license,
            'GPL-3.0': self._get_gpl_license,
            'BSD-3-Clause': self._get_bsd_license,
            'AGPL-3.0': self._get_agpl_license,
            'Custom-AI': self._get_custom_ai_license
        }
    
    def generate_license_pdf(self, github_url: str, license_type: str, repo_data: Dict) -> str:
        """Generate license PDF for repository"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"license_{license_type}_{timestamp}.pdf"
            
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Custom styles
            title_style = ParagraphStyle(
                'LicenseTitle',
                parent=styles['Title'],
                fontSize=20,
                textColor=blue,
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'LicenseHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=black,
                spaceAfter=12,
                spaceBefore=20
            )
            
            body_style = ParagraphStyle(
                'LicenseBody',
                parent=styles['Normal'],
                fontSize=11,
                alignment=TA_JUSTIFY,
                spaceAfter=12,
                leading=14
            )
            
            # Repository info header
            story.append(Paragraph(f"{license_type} License", title_style))
            story.append(Paragraph(f"Repository: {github_url}", body_style))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", body_style))
            story.append(Spacer(1, 30))
            
            # Copyright notice
            year = datetime.now().year
            copyright_text = f"Copyright (c) {year} {repo_data.get('owner', {}).get('login', 'Repository Owner')}"
            story.append(Paragraph(copyright_text, heading_style))
            story.append(Spacer(1, 20))
            
            # License text
            if license_type in self.licenses:
                license_content = self.licenses[license_type](repo_data)
            else:
                license_content = self._get_mit_license(repo_data)  # Default to MIT
            
            # Add license paragraphs
            for paragraph in license_content.split('\n\n'):
                if paragraph.strip():
                    story.append(Paragraph(paragraph.strip(), body_style))
                    story.append(Spacer(1, 12))
            
            # Add blockchain protection notice
            story.append(PageBreak())
            story.append(Paragraph("BLOCKCHAIN PROTECTION NOTICE", heading_style))
            
            protection_text = f"""This repository and its contents are protected by blockchain technology 
            and registered with Kreon Labs IP Protection System. Any unauthorized use, reproduction, or 
            distribution may result in legal action including DMCA takedown notices.
            
            Repository Hash: {repo_data.get('sha', 'N/A')}
            Registration Date: {datetime.now().strftime('%B %d, %Y')}
            Protection Level: Enhanced with C2PA metadata
            
            For licensing inquiries, please contact the repository owner through GitHub or 
            legal@kreonlabs.com for assistance with compliance verification."""
            
            story.append(Paragraph(protection_text, body_style))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"📄 License PDF generated: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error generating license PDF: {e}")
            raise
    
    def _get_mit_license(self, repo_data: Dict) -> str:
        """MIT License template"""
        return """Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""
    
    def _get_apache_license(self, repo_data: Dict) -> str:
        """Apache 2.0 License template"""
        return """Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""
    
    def _get_gpl_license(self, repo_data: Dict) -> str:
        """GPL-3.0 License template"""
        return """This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>."""
    
    def _get_bsd_license(self, repo_data: Dict) -> str:
        """BSD 3-Clause License template"""
        owner = repo_data.get('owner', {}).get('login', 'Repository Owner')
        return f"""Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of {owner} nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."""
    
    def _get_agpl_license(self, repo_data: Dict) -> str:
        """AGPL-3.0 License template"""
        return """This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

ADDITIONAL TERMS:
If you modify this Program, or any covered work, by linking or combining it
with proprietary software, the resulting work must be licensed under the AGPL."""
    
    def _get_custom_ai_license(self, repo_data: Dict) -> str:
        """Custom AI-friendly license template"""
        return """This software is provided under a Custom AI License with the following terms:

1. PERMITTED USES:
   - Personal and educational use
   - Commercial use with attribution
   - Modification and distribution of modified versions

2. RESTRICTIONS:
   - No use for training AI/ML models without explicit permission
   - No use in automated content generation systems
   - No use for creating competing products

3. ATTRIBUTION:
   - You must give appropriate credit to the original author(s)
   - Provide a link to the license and indicate changes made
   - Include the blockchain registration hash in any distribution

4. AI/ML TRAINING PROHIBITION:
   This software and its derivatives may NOT be used to train, fine-tune, or 
   otherwise improve artificial intelligence or machine learning models without 
   explicit written permission from the copyright holder.

5. WARRANTY DISCLAIMER:
   This software is provided "as is" without warranty of any kind.

For commercial licensing or AI training permissions, contact: legal@kreonlabs.com"""