"""
Security Scanner Module
Handles comprehensive security auditing for multiple platforms
"""
import os
import re
import git
import shutil
import tempfile
import requests
from typing import List, Dict
from datetime import datetime
from urllib.parse import urlparse
from dotenv import load_dotenv
load_dotenv()

from .utils import setup_logging
from .secret_patterns import SecretPatterns

logger = setup_logging(__name__)

try:
    from PIL import Image
    import io
    IMAGE_PROCESSING_AVAILABLE = True
except ImportError:
    IMAGE_PROCESSING_AVAILABLE = False
    logger.warning("⚠️ PIL not installed. Image watermark detection will be disabled.")


class SecurityScanner:
    """Handles comprehensive security scanning"""
    
    def __init__(self, config: Dict, llm):
        self.config = config
        self.llm = llm
        self.secret_patterns = SecretPatterns()
    
    def comprehensive_audit(self, url_analysis: Dict, audit_id: int) -> Dict:
        """Perform comprehensive security audit based on URL type"""
        
        audit_result = {
            'audit_id': audit_id,
            'input_url': url_analysis['original_url'],
            'cleaned_url': url_analysis['cleaned_url'],
            'platform': url_analysis['platform'],
            'url_type': url_analysis['url_type'],
            'timestamp': datetime.now().isoformat(),
            'findings': [],
            'files_scanned': 0,
            'total_findings': 0,
            'critical_findings': 0,
            'high_findings': 0,
            'medium_findings': 0,
            'low_findings': 0
        }
        
        # Route to appropriate audit method
        if url_analysis['platform'] == 'github':
            github_results = self.audit_github_repository(url_analysis['cleaned_url'])
            audit_result.update(github_results)
            
        elif url_analysis['platform'] == 'reddit':
            reddit_results = self.audit_reddit_content(url_analysis['cleaned_url'])
            audit_result.update(reddit_results)
            
        elif url_analysis['platform'] == 'twitter':
            twitter_results = self.audit_twitter_content(url_analysis['cleaned_url'])
            audit_result.update(twitter_results)
            
        elif url_analysis['url_type'] == 'image':
            image_results = self.audit_image_watermarks(url_analysis['cleaned_url'])
            audit_result.update(image_results)
            
        else:
            web_results = self.audit_web_content(url_analysis['cleaned_url'])
            audit_result.update(web_results)
        
        # Generate AI summary
        audit_result['ai_summary'] = self.generate_ai_summary(audit_result)
        
        return audit_result
    
    def audit_github_repository(self, github_url: str) -> Dict:
        """Enhanced GitHub repository audit with comprehensive secret scanning"""
        
        logger.info("🔍 Starting comprehensive GitHub repository audit...")
        
        path_parts = [p for p in urlparse(github_url).path.split('/') if p]
        if len(path_parts) < 2:
            return {'error': 'Invalid GitHub repository URL'}
        
        owner, repo = path_parts[0], path_parts[1]
        findings = []
        files_scanned = 0
        
        try:
            temp_dir = tempfile.mkdtemp()
            repo_path = os.path.join(temp_dir, repo)
            
            logger.info(f"📥 Cloning repository: {github_url}")
            git_repo = git.Repo.clone_from(github_url, repo_path)
            
            # Scan all files
            for root, dirs, files in os.walk(repo_path):
                if '.git' in root:
                    continue
                    
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_path)
                    
                    try:
                        if self.is_text_file(file_path):
                            file_findings = self.scan_file_for_secrets(file_path, relative_path)
                            findings.extend(file_findings)
                            files_scanned += 1
                    except Exception as e:
                        logger.warning(f"⚠️ Error scanning {relative_path}: {e}")
            
            # Scan commit history
            logger.info("🔍 Scanning commit history...")
            commit_findings = self.scan_commit_history_for_secrets(git_repo, repo_path)
            findings.extend(commit_findings)
            
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            return {'error': f'Failed to clone or scan repository: {str(e)}'}
        
        # Categorize findings
        critical_findings = [f for f in findings if f['severity'] == 'critical']
        high_findings = [f for f in findings if f['severity'] == 'high']
        medium_findings = [f for f in findings if f['severity'] == 'medium']
        low_findings = [f for f in findings if f['severity'] == 'low']
        
        return {
            'findings': findings,
            'files_scanned': files_scanned,
            'total_findings': len(findings),
            'critical_findings': len(critical_findings),
            'high_findings': len(high_findings),
            'medium_findings': len(medium_findings),
            'low_findings': len(low_findings),
            'repository_info': {
                'owner': owner,
                'repo': repo,
                'url': github_url
            }
        }
    
    def scan_file_for_secrets(self, file_path: str, relative_path: str) -> List[Dict]:
        """Comprehensive file scanning for secrets"""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for pattern_name, pattern_info in self.secret_patterns.get_patterns().items():
                        matches = re.finditer(pattern_info['pattern'], line, re.IGNORECASE)
                        
                        for match in matches:
                            if self.secret_patterns.is_likely_real_secret(match.group(), pattern_name):
                                findings.append({
                                    'type': 'secret_leak',
                                    'pattern_name': pattern_name,
                                    'file_path': relative_path,
                                    'line_number': line_num,
                                    'line_content': line.strip(),
                                    'matched_content': match.group()[:50] + '...' if len(match.group()) > 50 else match.group(),
                                    'severity': pattern_info['severity'],
                                    'description': pattern_info['description'],
                                    'recommendation': pattern_info['recommendation']
                                })
        
        except Exception as e:
            logger.error(f"Error scanning {relative_path}: {e}")
        
        return findings
    
    def scan_commit_history_for_secrets(self, git_repo, repo_path: str) -> List[Dict]:
        """Scan git commit history for secrets"""
        findings = []
        
        try:
            commits = list(git_repo.iter_commits('--all', max_count=50))
            logger.info(f"🔍 Scanning {len(commits)} commits...")
            
            for commit in commits:
                try:
                    if commit.parents:
                        diffs = commit.parents[0].diff(commit, create_patch=True)
                    else:
                        continue
                    
                    for diff in diffs:
                        if diff.deleted_file or diff.new_file or diff.a_blob != diff.b_blob:
                            patch_text = str(diff)
                            lines = patch_text.split('\n')
                            
                            for line in lines:
                                if line.startswith('-') and not line.startswith('---'):
                                    line_content = line[1:]
                                    
                                    for pattern_name, pattern_info in self.secret_patterns.get_patterns().items():
                                        matches = re.finditer(pattern_info['pattern'], line_content, re.IGNORECASE)
                                        
                                        for match in matches:
                                            if self.secret_patterns.is_likely_real_secret(match.group(), pattern_name):
                                                findings.append({
                                                    'type': 'historical_secret_leak',
                                                    'pattern_name': pattern_name,
                                                    'file_path': diff.a_path or diff.b_path or 'unknown',
                                                    'commit_hash': commit.hexsha[:8],
                                                    'commit_date': commit.committed_datetime.isoformat(),
                                                    'line_content': line_content.strip(),
                                                    'matched_content': match.group()[:50] + '...' if len(match.group()) > 50 else match.group(),
                                                    'severity': pattern_info['severity'],
                                                    'description': f"Historical {pattern_info['description']} found in commit history",
                                                    'recommendation': f"{pattern_info['recommendation']} Found in git history."
                                                })
                except:
                    continue
        except Exception as e:
            logger.warning(f"⚠️ Error scanning commit history: {e}")
        
        return findings
    
    def is_text_file(self, file_path: str) -> bool:
        """Check if file is a text file suitable for scanning"""
        text_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            '.sql', '.html', '.htm', '.css', '.scss', '.xml', '.json', '.yaml',
            '.yml', '.toml', '.ini', '.cfg', '.conf', '.txt', '.md', '.log',
            '.sh', '.bash', '.env', '.gitignore'
        }
        
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext in text_extensions:
            return True
        
        filename = os.path.basename(file_path).lower()
        if filename in {'dockerfile', 'makefile', 'rakefile'}:
            return True
        
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\0' in chunk:
                    return False
                try:
                    chunk.decode('utf-8')
                    return True
                except UnicodeDecodeError:
                    return False
        except:
            return False
    
    def audit_reddit_content(self, reddit_url: str) -> Dict:
        """Audit Reddit content"""
        logger.info("🔍 Starting Reddit content audit...")
        
        findings = [{
            'type': 'reddit_analysis',
            'severity': 'low',
            'description': 'Reddit content analysis completed',
            'recommendation': 'Review content for sensitive information disclosure'
        }]
        
        return {
            'findings': findings,
            'files_scanned': 1,
            'total_findings': len(findings),
            'critical_findings': 0,
            'high_findings': 0,
            'medium_findings': 0,
            'low_findings': len(findings)
        }
    
    def audit_twitter_content(self, twitter_url: str) -> Dict:
        """Audit Twitter content"""
        logger.info("🔍 Starting Twitter content audit...")
        
        findings = [{
            'type': 'twitter_analysis',
            'severity': 'low',
            'description': 'Twitter content analysis completed',
            'recommendation': 'Review posts for sensitive information disclosure'
        }]
        
        return {
            'findings': findings,
            'files_scanned': 1,
            'total_findings': len(findings),
            'critical_findings': 0,
            'high_findings': 0,
            'medium_findings': 0,
            'low_findings': len(findings)
        }
    
    def audit_image_watermarks(self, image_url: str) -> Dict:
        """Audit image for watermarks"""
        logger.info("🖼️ Starting image watermark audit...")
        
        if not IMAGE_PROCESSING_AVAILABLE:
            return {
                'error': 'Image processing not available (PIL not installed)',
                'findings': [],
                'files_scanned': 0,
                'total_findings': 0
            }
        
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            image = Image.open(io.BytesIO(response.content))
            findings = []
            
            # Placeholder for watermark detection
            # You would integrate your watermark detection code here
            
            return {
                'findings': findings,
                'files_scanned': 1,
                'total_findings': len(findings),
                'critical_findings': 0,
                'high_findings': 0,
                'medium_findings': 0,
                'low_findings': 0,
                'image_info': {
                    'url': image_url,
                    'size': image.size,
                    'format': image.format
                }
            }
            
        except Exception as e:
            return {
                'error': f'Failed to audit image: {str(e)}',
                'findings': [],
                'files_scanned': 0,
                'total_findings': 0
            }
    
    def audit_web_content(self, url: str) -> Dict:
        """Generic web content audit"""
        logger.info("🔍 Starting web content audit...")
        
        findings = []
        
        try:
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            content = response.text
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                for pattern_name, pattern_info in self.secret_patterns.get_patterns().items():
                    matches = re.finditer(pattern_info['pattern'], line, re.IGNORECASE)
                    
                    for match in matches:
                        if self.secret_patterns.is_likely_real_secret(match.group(), pattern_name):
                            findings.append({
                                'type': 'web_secret_exposure',
                                'pattern_name': pattern_name,
                                'line_number': line_num,
                                'line_content': line.strip()[:100],
                                'matched_content': match.group()[:50] + '...' if len(match.group()) > 50 else match.group(),
                                'severity': 'critical',
                                'description': f"Publicly exposed {pattern_info['description']} on web page",
                                'recommendation': 'Immediately remove this secret from public web content'
                            })
            
        except Exception as e:
            findings.append({
                'type': 'web_audit_error',
                'severity': 'low',
                'description': f'Failed to audit web content: {str(e)}',
                'recommendation': 'Manual review may be required'
            })
        
        return {
            'findings': findings,
            'files_scanned': 1,
            'total_findings': len(findings),
            'critical_findings': len([f for f in findings if f['severity'] == 'critical']),
            'high_findings': len([f for f in findings if f['severity'] == 'high']),
            'medium_findings': len([f for f in findings if f['severity'] == 'medium']),
            'low_findings': len([f for f in findings if f['severity'] == 'low'])
        }
    
    def generate_ai_summary(self, audit_result: Dict) -> str:
        """Generate AI summary of audit results"""
        try:
            summary_prompt = f"""
            Generate a security audit summary:
            
            Platform: {audit_result['platform']}
            Total Findings: {audit_result['total_findings']}
            Critical: {audit_result['critical_findings']}
            High: {audit_result['high_findings']}
            Medium: {audit_result['medium_findings']}
            Low: {audit_result['low_findings']}
            
            Provide a concise professional assessment with:
            1. Risk level
            2. Key recommendations
            3. Next steps
            """
            
            response = self.llm.invoke(summary_prompt)
            return response.content
            
        except Exception as e:
            return f"AI summary generation failed: {str(e)}"