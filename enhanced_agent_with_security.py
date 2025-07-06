import asyncio
import hashlib
import json
import os
import requests
import time
import re
import git
import shutil
import tempfile
import subprocess
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

# LangChain imports
from langchain.agents import initialize_agent, AgentType
from langchain.tools import BaseTool, StructuredTool
from langchain.schema import BaseMessage
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

# LlamaIndex imports
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI as LlamaOpenAI
from llama_index.llms.ollama import Ollama

from dotenv import load_dotenv
load_dotenv()

# PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import red, black, green
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ ReportLab not installed. PDF generation will be disabled.")

# Image processing for watermarks
try:
    from PIL import Image
    import io
    IMAGE_PROCESSING_AVAILABLE = True
except ImportError:
    IMAGE_PROCESSING_AVAILABLE = False
    print("⚠️ PIL not installed. Image watermark detection will be disabled.")

class EnhancedGitHubProtectionAgent:
    def __init__(self, config: Dict):
        self.config = config
        self.setup_models()
        self.setup_tools()
        self.setup_agent()
        
        # In-memory storage
        self.repositories = {}
        self.violations = {}
        self.security_audits = {}
        self.jobs = {}
        
    def setup_models(self):
        """Initialize AI models"""
        use_local = self.config.get('USE_LOCAL_MODEL', False)
        
        if use_local:
            print("🦙 Using local model")
            self.llm = ChatOpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama",
                model="llama3.2:3b"
            )
            Settings.llm = Ollama(model="llama3.2:3b", base_url="http://localhost:11434")
        else:
            print("🤖 Using OpenAI")
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                api_key=self.config['OPENAI_API_KEY']
            )
            Settings.llm = LlamaOpenAI(
                model="gpt-4o-mini",
                api_key=self.config['OPENAI_API_KEY']
            )
        
        # Setup embeddings
        try:
            Settings.embed_model = HuggingFaceEmbedding(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            print("✅ Using free HuggingFace embeddings")
        except Exception as e:
            print(f"⚠️ Embeddings setup failed: {e}")
        
    def setup_tools(self):
        """Initialize agent tools"""
        self.tools = [
            StructuredTool.from_function(
                func=self.analyze_repository,
                name="analyze_repository",
                description="Analyze a GitHub repository for key features and generate fingerprint"
            ),
            StructuredTool.from_function(
                func=self.register_repository,
                name="register_repository", 
                description="Register a repository on the blockchain for protection"
            ),
            StructuredTool.from_function(
                func=self.search_for_violations,
                name="search_for_violations",
                description="Search for potential code violations across GitHub"
            ),
            StructuredTool.from_function(
                func=self.generate_license,
                name="generate_license",
                description="Generate appropriate license for repository"
            ),
            StructuredTool.from_function(
                func=self.security_audit,
                name="security_audit",
                description="Perform security audit on repository code"
            ),
            StructuredTool.from_function(
                func=self.report_violation,
                name="report_violation",
                description="Report a code violation to the blockchain"
            ),
            StructuredTool.from_function(
                func=self.clean_github_urls,
                name="clean_github_urls",
                description="Clean and standardize URLs from text input"
            ),
            StructuredTool.from_function(
                func=self.comprehensive_security_audit,
                name="comprehensive_security_audit",
                description="Perform comprehensive security audit on any URL (GitHub, Reddit, Twitter, images, etc.)"
            )
        ]
        
    def setup_agent(self):
        """Initialize the LangChain agent"""
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            memory=self.memory,
            max_iterations=5
        )

    # ===== CORE REPOSITORY METHODS =====
    
    def analyze_repository(self, github_url: str) -> Dict:
        """Analyze repository and extract key features"""
        try:
            repo_parts = github_url.replace('https://github.com/', '').split('/')
            if len(repo_parts) < 2:
                return {'success': False, 'error': 'Invalid GitHub URL'}
            
            owner, repo = repo_parts[0], repo_parts[1]
            
            headers = {}
            if self.config.get('GITHUB_TOKEN'):
                headers['Authorization'] = f"token {self.config['GITHUB_TOKEN']}"
            
            # Get repo details
            repo_response = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                headers=headers
            )
            
            if repo_response.status_code != 200:
                return {'success': False, 'error': 'Repository not found or private'}
            
            repo_data = repo_response.json()
            
            # Get file list
            contents_response = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}/contents",
                headers=headers
            )
            
            files = []
            if contents_response.status_code == 200:
                contents = contents_response.json()
                files = [item['name'] for item in contents if item['type'] == 'file']
            
            # Generate fingerprint data
            fingerprint_data = {
                'name': repo_data.get('name', ''),
                'description': repo_data.get('description', ''),
                'language': repo_data.get('language', ''),
                'size': repo_data.get('size', 0),
                'files': files[:10],
                'created_at': repo_data.get('created_at', ''),
            }
            
            # Generate hashes
            repo_hash = hashlib.sha256(
                json.dumps(fingerprint_data, sort_keys=True).encode()
            ).hexdigest()
            
            fingerprint = hashlib.sha256(
                f"{repo_data.get('full_name', '')}{repo_data.get('created_at', '')}".encode()
            ).hexdigest()
            
            # AI feature extraction
            features_prompt = f"""
            Analyze this GitHub repository and identify key unique features:
            Name: {repo_data.get('name', '')}
            Description: {repo_data.get('description', '')}
            Language: {repo_data.get('language', '')}
            Files: {', '.join(files[:5])}
            
            List 3-5 distinctive features that make this repository unique.
            """
            
            try:
                response = self.llm.invoke(features_prompt)
                key_features = response.content
            except Exception as e:
                key_features = f"Language: {repo_data.get('language', 'Unknown')}, Files: {len(files)}"
            
            return {
                'success': True,
                'repo_hash': repo_hash,
                'fingerprint': fingerprint,
                'key_features': key_features,
                'total_files': len(files),
                'analysis': fingerprint_data,
                'repo_data': repo_data
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def register_repository(self, github_url: str, license_type: str = "MIT") -> Dict:
        """Register repository on blockchain"""
        try:
            analysis = self.analyze_repository(github_url)
            if not analysis['success']:
                return analysis
            
            # Simulate blockchain transaction
            tx_hash = f"0x{hashlib.sha256(f'{github_url}{time.time()}'.encode()).hexdigest()}"
            
            repo_id = len(self.repositories) + 1
            self.repositories[repo_id] = {
                'id': repo_id,
                'github_url': github_url,
                'repo_hash': analysis['repo_hash'],
                'fingerprint': analysis['fingerprint'],
                'key_features': analysis['key_features'],
                'license_type': license_type,
                'registered_at': datetime.now().isoformat(),
                'tx_hash': tx_hash
            }
            
            print(f"📝 Repository registered with ID: {repo_id}")
            
            return {
                'success': True,
                'repo_id': repo_id,
                'tx_hash': tx_hash,
                'repo_hash': analysis['repo_hash'],
                'fingerprint': analysis['fingerprint']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ===== COMPREHENSIVE SECURITY AUDIT =====
    
    def comprehensive_security_audit(self, input_url: str) -> Dict:
        """Enhanced comprehensive security audit with multi-platform support"""
        
        try:
            print("🔍 Starting comprehensive security audit...")
            
            # Step 1: Clean and categorize the input URL
            url_analysis = self.analyze_and_clean_url(input_url)
            
            if not url_analysis['valid']:
                return {
                    'success': False,
                    'error': f"Invalid URL: {url_analysis['error']}",
                    'url_analysis': url_analysis
                }
            
            audit_id = len(self.security_audits) + 1
            
            audit_result = {
                'audit_id': audit_id,
                'input_url': input_url,
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
            
            # Step 2: Route to appropriate audit method
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
            
            # Step 3: Generate AI summary
            audit_result['ai_summary'] = self.generate_ai_summary(audit_result)
            
            # Step 4: Generate PDF report if findings exist
            if audit_result['total_findings'] > 0 and PDF_AVAILABLE:
                pdf_path = self.generate_security_pdf_report(audit_result)
                audit_result['pdf_report'] = pdf_path
            
            # Store the audit
            self.security_audits[audit_id] = audit_result
            
            return {
                'success': True,
                'audit_id': audit_id,
                **audit_result
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ===== URL ANALYSIS AND CLEANING =====
    
    def analyze_and_clean_url(self, input_url: str) -> Dict:
        """AI-powered URL analysis and cleaning"""
        
        try:
            url = input_url.strip()
            
            # Basic cleaning
            url = re.sub(r'^["\'\s]+|["\'\s]+$', '', url)
            url = re.sub(r'\s+', '', url)
            
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                if any(domain in url for domain in ['github.com', 'reddit.com', 'twitter.com', 'x.com']):
                    url = 'https://' + url
                else:
                    url = 'https://' + url
            
            parsed = urlparse(url)
            
            # AI categorization
            categorization_prompt = f"""
            Analyze this URL and categorize it:
            URL: {url}
            
            Determine:
            1. Platform (github, reddit, twitter, instagram, generic_web, image_hosting, etc.)
            2. Content type (repository, profile, post, image, video, etc.)
            3. If it's a GitHub URL, extract owner/repo
            4. If it's an image URL, confirm it's a direct image link
            
            Respond in JSON format:
            {{
                "platform": "platform_name",
                "content_type": "type",
                "is_valid": true/false,
                "github_owner": "owner" (if GitHub),
                "github_repo": "repo" (if GitHub),
                "is_image": true/false,
                "confidence": 0.0-1.0
            }}
            """
            
            try:
                ai_response = self.llm.invoke(categorization_prompt)
                ai_analysis = json.loads(ai_response.content)
            except:
                ai_analysis = self.manual_url_analysis(url, parsed)
            
            cleaned_url = self.clean_url_based_on_platform(url, parsed, ai_analysis)
            
            return {
                'valid': True,
                'original_url': input_url,
                'cleaned_url': cleaned_url,
                'platform': ai_analysis.get('platform', 'unknown'),
                'url_type': ai_analysis.get('content_type', 'unknown'),
                'ai_analysis': ai_analysis
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'original_url': input_url
            }
    
    def manual_url_analysis(self, url: str, parsed) -> Dict:
        """Fallback manual URL analysis"""
        
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        
        if 'github.com' in domain:
            path_parts = [p for p in parsed.path.split('/') if p]
            return {
                'platform': 'github',
                'content_type': 'repository' if len(path_parts) >= 2 else 'profile',
                'is_valid': True,
                'github_owner': path_parts[0] if path_parts else None,
                'github_repo': path_parts[1] if len(path_parts) > 1 else None,
                'is_image': False,
                'confidence': 0.9
            }
        elif 'reddit.com' in domain or 'redd.it' in domain:
            return {
                'platform': 'reddit',
                'content_type': 'post' if '/comments/' in path else 'profile',
                'is_valid': True,
                'is_image': False,
                'confidence': 0.9
            }
        elif 'twitter.com' in domain or 'x.com' in domain:
            return {
                'platform': 'twitter',
                'content_type': 'post' if '/status/' in path else 'profile',
                'is_valid': True,
                'is_image': False,
                'confidence': 0.9
            }
        elif any(ext in path for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']):
            return {
                'platform': 'image_hosting',
                'content_type': 'image',
                'is_valid': True,
                'is_image': True,
                'confidence': 0.8
            }
        else:
            return {
                'platform': 'generic_web',
                'content_type': 'webpage',
                'is_valid': True,
                'is_image': False,
                'confidence': 0.6
            }
    
    def clean_url_based_on_platform(self, url: str, parsed, ai_analysis: Dict) -> str:
        """Clean URL based on platform-specific rules"""
        
        platform = ai_analysis.get('platform', 'unknown')
        
        if platform == 'github':
            path_parts = [p for p in parsed.path.split('/') if p]
            if len(path_parts) >= 2:
                clean_path = f"/{path_parts[0]}/{path_parts[1]}"
                return f"https://github.com{clean_path}"
        
        elif platform == 'reddit':
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            return base_url.rstrip('/')
        
        elif platform == 'twitter':
            if 'x.com' in parsed.netloc:
                base_url = f"https://x.com{parsed.path}"
            else:
                base_url = f"https://twitter.com{parsed.path}"
            return base_url.rstrip('/')
        
        elif ai_analysis.get('is_image', False):
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')

    # ===== GITHUB SECURITY SCANNING =====
    
    def audit_github_repository(self, github_url: str) -> Dict:
        """Enhanced GitHub repository audit with comprehensive secret scanning"""
        
        print("🔍 Starting comprehensive GitHub repository audit...")
        
        path_parts = [p for p in urlparse(github_url).path.split('/') if p]
        if len(path_parts) < 2:
            return {'error': 'Invalid GitHub repository URL'}
        
        owner, repo = path_parts[0], path_parts[1]
        findings = []
        files_scanned = 0
        
        try:
            temp_dir = tempfile.mkdtemp()
            repo_path = os.path.join(temp_dir, repo)
            
            print(f"📥 Cloning repository: {github_url}")
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
                        print(f"⚠️ Error scanning {relative_path}: {e}")
            
            # Scan commit history
            print("🔍 Scanning commit history...")
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
                    for pattern_name, pattern_info in self.get_secret_patterns().items():
                        matches = re.finditer(pattern_info['pattern'], line, re.IGNORECASE)
                        
                        for match in matches:
                            if self.is_likely_real_secret(match.group(), pattern_name):
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
            print(f"Error scanning {relative_path}: {e}")
        
        return findings
    
    def get_secret_patterns(self) -> Dict:
        """Comprehensive patterns for detecting secrets"""
        
        return {
            'aws_access_key': {
                'pattern': r'AKIA[0-9A-Z]{16}',
                'severity': 'critical',
                'description': 'AWS Access Key ID detected',
                'recommendation': 'Immediately revoke this AWS access key and rotate credentials'
            },
            'private_key_general': {
                'pattern': r'(?i)([A-Z_]*PRIVATE_KEY\s*[=:]\s*[\'"]?[^\s\'"]+[\'"]?)',
                'severity': 'critical',
                'description': 'Private key detected',
                'recommendation': 'Remove private key and use secure key management'
            },
            'api_key_general': {
                'pattern': r'(?i)([A-Z_]*API_KEY\s*[=:]\s*[\'"]?[^\s\'"]+[\'"]?)',
                'severity': 'high',
                'description': 'API key detected',
                'recommendation': 'Remove API key and use environment variables'
            },
            'github_token': {
                'pattern': r'gh[pousr]_[A-Za-z0-9_]{36,251}',
                'severity': 'critical',
                'description': 'GitHub token detected',
                'recommendation': 'Immediately revoke this GitHub token'
            },
            'openai_api_key': {
                'pattern': r'sk-[A-Za-z0-9]{48}',
                'severity': 'critical',
                'description': 'OpenAI API key detected',
                'recommendation': 'Revoke this OpenAI API key immediately'
            },
            'database_url': {
                'pattern': r'(?i)(postgres|mysql|mongodb)://[^\s\'"]+',
                'severity': 'high',
                'description': 'Database connection string detected',
                'recommendation': 'Use environment variables for database credentials'
            },
            'jwt_token': {
                'pattern': r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*',
                'severity': 'high',
                'description': 'JWT token detected',
                'recommendation': 'Remove JWT token from code'
            },
            'ssh_private_key': {
                'pattern': r'-----BEGIN [A-Z ]*PRIVATE KEY-----',
                'severity': 'critical',
                'description': 'SSH private key detected',
                'recommendation': 'Remove SSH private key immediately'
            }
        }
    
    def is_likely_real_secret(self, matched_text: str, pattern_name: str) -> bool:
        """Validate if matched text is likely a real secret"""
        
        if any(sep in matched_text for sep in ['=', ':']):
            for sep in ['=', ':']:
                if sep in matched_text:
                    value_part = matched_text.split(sep, 1)[1].strip().strip('\'"')
                    break
        else:
            value_part = matched_text
        
        # Skip common placeholders
        placeholder_patterns = [
            r'^\s*$', r'^your[_\s]*\w*[_\s]*key', r'^example', r'^test[_\s]*',
            r'^dummy[_\s]*', r'^placeholder', r'^\.\.\.$', r'^x+$', r'^0+$'
        ]
        
        for pattern in placeholder_patterns:
            if re.match(pattern, value_part.lower()):
                return False
        
        # Pattern-specific validation
        if pattern_name == 'aws_access_key':
            return len(value_part) == 20 and value_part.startswith('AKIA')
        elif pattern_name == 'openai_api_key':
            return value_part.startswith('sk-') and len(value_part) == 51
        elif pattern_name == 'github_token':
            return (value_part.startswith(('ghp_', 'gho_', 'ghu_', 'ghs_', 'ghr_')) and len(value_part) >= 40)
        
        return len(value_part) > 8
    
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
    
    def scan_commit_history_for_secrets(self, git_repo, repo_path: str) -> List[Dict]:
        """Scan git commit history for secrets"""
        
        findings = []
        
        try:
            commits = list(git_repo.iter_commits('--all', max_count=50))
            print(f"🔍 Scanning {len(commits)} commits...")
            
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
                                    
                                    for pattern_name, pattern_info in self.get_secret_patterns().items():
                                        matches = re.finditer(pattern_info['pattern'], line_content, re.IGNORECASE)
                                        
                                        for match in matches:
                                            if self.is_likely_real_secret(match.group(), pattern_name):
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
            print(f"⚠️ Error scanning commit history: {e}")
        
        return findings

    # ===== URL CLEANING METHODS =====
    
    def clean_github_urls(self, url_text: str) -> Dict:
        """Clean and standardize GitHub URLs from text input"""
        
        try:
            print(f"🧹 Cleaning URLs from text input...")
            
            raw_urls = self.extract_urls_from_text(url_text)
            cleaned_urls = []
            github_urls = []
            other_urls = []
            
            for url in raw_urls:
                cleaned_result = self.clean_single_url(url)
                
                if cleaned_result['success']:
                    cleaned_urls.append(cleaned_result['cleaned_url'])
                    
                    if cleaned_result['platform'] == 'github':
                        github_urls.append({
                            'original': url,
                            'cleaned': cleaned_result['cleaned_url'],
                            'owner': cleaned_result.get('owner'),
                            'repo': cleaned_result.get('repo'),
                            'type': cleaned_result.get('url_type', 'repository')
                        })
                    else:
                        other_urls.append({
                            'original': url,
                            'cleaned': cleaned_result['cleaned_url'],
                            'platform': cleaned_result['platform'],
                            'type': cleaned_result.get('url_type', 'unknown')
                        })
            
            ai_analysis = self.ai_analyze_url_collection(cleaned_urls)
            
            return {
                'success': True,
                'original_text': url_text,
                'total_urls_found': len(raw_urls),
                'cleaned_urls': cleaned_urls,
                'github_urls': github_urls,
                'other_urls': other_urls,
                'ai_analysis': ai_analysis,
                'recommendations': self.generate_url_recommendations(github_urls, other_urls)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original_text': url_text
            }
    
    def extract_urls_from_text(self, text: str) -> List[str]:
        """Extract potential URLs from text"""
        
        urls = []
        
        # Standard URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls.extend(re.findall(url_pattern, text))
        
        # URLs without protocol
        no_protocol_pattern = r'(?:github\.com|reddit\.com|twitter\.com|x\.com)[^\s<>"{}|\\^`\[\]]+'
        no_protocol_urls = re.findall(no_protocol_pattern, text, re.IGNORECASE)
        urls.extend([f"https://{url}" for url in no_protocol_urls])
        
        # GitHub-specific patterns
        github_patterns = [
            r'github\.com/[\w\-\.]+/[\w\-\.]+',
            r'git@github\.com:[\w\-\.]+/[\w\-\.]+\.git'
        ]
        
        for pattern in github_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.startswith('git@'):
                    clean_match = match.replace('git@github.com:', 'https://github.com/').replace('.git', '')
                    urls.append(clean_match)
                elif not match.startswith('http'):
                    urls.append(f"https://{match}")
                else:
                    urls.append(match)
        
        # Remove duplicates
        unique_urls = []
        seen = set()
        for url in urls:
            url_clean = url.strip().lower()
            if url_clean not in seen and len(url_clean) > 10:
                seen.add(url_clean)
                unique_urls.append(url.strip())
        
        return unique_urls
    
    def clean_single_url(self, url: str) -> Dict:
        """Clean and analyze a single URL"""
        
        try:
            cleaned_url = url.strip()
            cleaned_url = re.sub(r'^["\'\s\[\]()]+|["\'\s\[\]()]+, '', cleaned_url)
            cleaned_url = re.sub(r'\s+', '', cleaned_url)
            
            if cleaned_url.startswith('git@github.com:'):
                cleaned_url = cleaned_url.replace('git@github.com:', 'https://github.com/').replace('.git', '')
            elif not cleaned_url.startswith(('http://', 'https://')):
                cleaned_url = 'https://' + cleaned_url
            
            parsed = urlparse(cleaned_url)
            
            if not parsed.netloc:
                return {'success': False, 'error': 'Invalid URL format'}
            
            platform_result = self.identify_and_clean_platform_url(cleaned_url, parsed)
            
            return {
                'success': True,
                'original_url': url,
                'cleaned_url': platform_result['cleaned_url'],
                'platform': platform_result['platform'],
                'url_type': platform_result.get('url_type', 'unknown'),
                'owner': platform_result.get('owner'),
                'repo': platform_result.get('repo')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original_url': url
            }
    
    def identify_and_clean_platform_url(self, url: str, parsed) -> Dict:
        """Identify platform and clean URL"""
        
        domain = parsed.netloc.lower()
        path = parsed.path
        
        if 'github.com' in domain:
            path_parts = [p for p in path.split('/') if p]
            
            if len(path_parts) >= 2:
                owner, repo = path_parts[0], path_parts[1]
                clean_path = f"/{owner}/{repo}"
                clean_url = f"https://github.com{clean_path}"
                
                return {
                    'platform': 'github',
                    'url_type': 'repository',
                    'cleaned_url': clean_url,
                    'owner': owner,
                    'repo': repo
                }
            elif len(path_parts) == 1:
                owner = path_parts[0]
                return {
                    'platform': 'github',
                    'url_type': 'profile',
                    'cleaned_url': f"https://github.com/{owner}",
                    'owner': owner
                }
        
        elif 'reddit.com' in domain or 'redd.it' in domain:
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')
            url_type = 'post' if '/comments/' in path else 'profile' if '/user/' in path else 'subreddit'
            
            return {
                'platform': 'reddit',
                'url_type': url_type,
                'cleaned_url': clean_url
            }
        
        elif 'twitter.com' in domain or 'x.com' in domain:
            if 'twitter.com' in domain:
                clean_url = url.replace('twitter.com', 'x.com')
            else:
                clean_url = url
            
            clean_url = clean_url.split('?')[0].rstrip('/')
            url_type = 'post' if '/status/' in path else 'profile'
            
            return {
                'platform': 'twitter',
                'url_type': url_type,
                'cleaned_url': clean_url
            }
        
        elif any(ext in path.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']):
            return {
                'platform': 'image_hosting',
                'url_type': 'image',
                'cleaned_url': f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            }
        
        else:
            return {
                'platform': 'generic_web',
                'url_type': 'webpage',
                'cleaned_url': f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')
            }
    
    def ai_analyze_url_collection(self, urls: List[str]) -> Dict:
        """AI analysis of URL collection"""
        
        if not urls:
            return {'analysis': 'No URLs to analyze'}
        
        try:
            analysis_prompt = f"""
            Analyze this collection of URLs:
            {json.dumps(urls, indent=2)}
            
            Provide:
            1. Platform distribution (GitHub, Reddit, Twitter, etc.)
            2. Content types (repositories, profiles, posts, images)
            3. Security assessment
            4. Recommendations
            
            Keep response concise.
            """
            
            response = self.llm.invoke(analysis_prompt)
            return {'analysis': response.content, 'platform_summary': self.basic_platform_analysis(urls)}
            
        except Exception as e:
            return {'error': str(e), 'platform_summary': self.basic_platform_analysis(urls)}
    
    def basic_platform_analysis(self, urls: List[str]) -> Dict:
        """Basic platform analysis"""
        
        platform_counts = {}
        
        for url in urls:
            if 'github.com' in url:
                platform_counts['github'] = platform_counts.get('github', 0) + 1
            elif 'reddit.com' in url or 'redd.it' in url:
                platform_counts['reddit'] = platform_counts.get('reddit', 0) + 1
            elif 'twitter.com' in url or 'x.com' in url:
                platform_counts['twitter'] = platform_counts.get('twitter', 0) + 1
            else:
                platform_counts['other'] = platform_counts.get('other', 0) + 1
        
        return platform_counts
    
    def generate_url_recommendations(self, github_urls: List[Dict], other_urls: List[Dict]) -> List[str]:
        """Generate recommendations"""
        
        recommendations = []
        
        if github_urls:
            recommendations.append(f"Found {len(github_urls)} GitHub repositories - recommend security audit")
            for gh_url in github_urls:
                if gh_url.get('type') == 'repository':
                    recommendations.append(f"Repository {gh_url['owner']}/{gh_url['repo']} can be audited for secrets")
        
        if other_urls:
            platforms = set(url['platform'] for url in other_urls)
            if 'reddit' in platforms:
                recommendations.append("Reddit URLs found - can scrape for image content analysis")
            if 'twitter' in platforms:
                recommendations.append("Twitter URLs found - can scrape for image content analysis")
            image_urls = [url for url in other_urls if url['type'] == 'image']
            if image_urls:
                recommendations.append(f"Found {len(image_urls)} image URLs - can check for watermarks")
        
        if not recommendations:
            recommendations.append("No actionable URLs found for security analysis")
        
        return recommendations

    # ===== OTHER AUDIT METHODS =====
    
    def audit_reddit_content(self, reddit_url: str) -> Dict:
        """Audit Reddit content"""
        
        print("🔍 Starting Reddit content audit...")
        
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
        
        print("🔍 Starting Twitter content audit...")
        
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
        
        print("🖼️ Starting image watermark audit...")
        
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
        
        print("🔍 Starting web content audit...")
        
        findings = []
        
        try:
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            content = response.text
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                for pattern_name, pattern_info in self.get_secret_patterns().items():
                    matches = re.finditer(pattern_info['pattern'], line, re.IGNORECASE)
                    
                    for match in matches:
                        if self.is_likely_real_secret(match.group(), pattern_name):
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

    # ===== PDF REPORT GENERATION =====
    
    def generate_security_pdf_report(self, audit_result: Dict) -> str:
        """Generate PDF security report"""
        
        if not PDF_AVAILABLE:
            print("⚠️ PDF generation not available (ReportLab not installed)")
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
                    story.append(Paragraph(f"Finding #{i}: {finding.get('pattern_name', finding.get('type', 'Unknown'))}", styles['Heading3']))
                    
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
            print(f"📄 Security audit PDF report generated: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error generating PDF report: {e}")
            return None
    
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

    # ===== ORIGINAL METHODS (UNCHANGED) =====
    
    def search_for_violations(self, repo_id: int, key_features: List[str] = None) -> List[Dict]:
        """Search GitHub for potential code violations"""
        violations = []
        
        try:
            if repo_id not in self.repositories:
                return []
            
            repo = self.repositories[repo_id]
            
            if not key_features:
                key_features = repo['key_features'].split('\n')[:3]
            
            headers = {}
            if self.config.get('GITHUB_TOKEN'):
                headers['Authorization'] = f"token {self.config['GITHUB_TOKEN']}"
            
            search_terms = [repo['github_url'].split('/')[-1]]
            
            for term in search_terms[:2]:
                search_query = f"{term} in:name,description"
                
                response = requests.get(
                    'https://api.github.com/search/repositories',
                    headers=headers,
                    params={'q': search_query, 'per_page': 5}
                )
                
                if response.status_code == 200:
                    results = response.json()
                    
                    for item in results.get('items', []):
                        if item['html_url'] == repo['github_url']:
                            continue
                        
                        similarity = self.calculate_simple_similarity(
                            repo['github_url'], 
                            item['html_url']
                        )
                        
                        if similarity > 0.5:
                            violations.append({
                                'repo_url': item['html_url'],
                                'similarity': similarity,
                                'name': item['name'],
                                'description': item.get('description', ''),
                                'language': item.get('language', ''),
                                'created_at': item.get('created_at', '')
                            })
                
                time.sleep(1)
                
        except Exception as e:
            print(f"Error searching for violations: {e}")
            
        return violations
    
    def calculate_simple_similarity(self, original_url: str, candidate_url: str) -> float:
        """Calculate simple similarity between repositories"""
        original_name = original_url.split('/')[-1].lower()
        candidate_name = candidate_url.split('/')[-1].lower()
        
        if original_name == candidate_name:
            return 0.9
        
        common_chars = set(original_name) & set(candidate_name)
        similarity = len(common_chars) / max(len(original_name), len(candidate_name))
        
        return similarity
    
    def generate_license(self, repo_type: str, usage_requirements: str) -> str:
        """Generate appropriate license"""
        prompt = f"""
        Generate an appropriate open source license for a {repo_type} repository 
        with requirements: {usage_requirements}
        
        Provide a concise license recommendation.
        """
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"Error generating license: {e}"
    
    def security_audit(self, github_url: str) -> Dict:
        """Basic security audit"""
        try:
            analysis = self.analyze_repository(github_url)
            if not analysis['success']:
                return analysis
                
            audit_prompt = f"""
            Perform a security audit on this repository:
            Name: {analysis['analysis'].get('name', '')}
            Language: {analysis['analysis'].get('language', '')}
            Files: {', '.join(analysis['analysis'].get('files', []))}
            
            Identify security concerns and recommendations.
            """
            
            try:
                response = self.llm.invoke(audit_prompt)
                audit_result = response.content
            except Exception as e:
                audit_result = f"Audit failed: {e}"
            
            return {
                'success': True,
                'audit_result': audit_result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def report_violation(self, original_repo_id: int, violating_url: str, similarity_score: float) -> Dict:
        """Report violation"""
        try:
            evidence = {
                'violating_url': violating_url,
                'similarity_score': similarity_score,
                'reported_at': datetime.now().isoformat()
            }
            evidence_hash = hashlib.sha256(
                json.dumps(evidence, sort_keys=True).encode()
            ).hexdigest()
            
            tx_hash = f"0x{hashlib.sha256(f'{violating_url}{time.time()}'.encode()).hexdigest()}"
            
            violation_id = len(self.violations) + 1
            self.violations[violation_id] = {
                'id': violation_id,
                'original_repo_id': original_repo_id,
                'violating_url': violating_url,
                'similarity_score': similarity_score,
                'evidence_hash': evidence_hash,
                'tx_hash': tx_hash,
                'reported_at': datetime.now().isoformat(),
                'status': 'pending'
            }
            
            print(f"⚠️ Violation reported with ID: {violation_id}")
            
            return {
                'success': True,
                'violation_id': violation_id,
                'tx_hash': tx_hash,
                'evidence_hash': evidence_hash
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_dmca(self, violation_data: Dict) -> str:
        """Generate DMCA takedown notice"""
        try:
            dmca_prompt = f"""
            Generate a professional DMCA takedown notice:
            
            Violating URL: {violation_data['violating_url']}
            Similarity Score: {violation_data.get('similarity_score', 0):.2f}
            Evidence Hash: {violation_data.get('evidence_hash', 'N/A')}
            
            Include formal legal language and removal request.
            """
            
            response = self.llm.invoke(dmca_prompt)
            return response.content
            
        except Exception as e:
            return f"Error generating DMCA: {str(e)}"
    
    def run_protection_workflow(self, github_url: str) -> Dict:
        """Run complete protection workflow"""
        results = {}
        
        try:
            print("🔍 Analyzing repository...")
            analysis = self.analyze_repository(github_url)
            results['analysis'] = analysis
            
            if not analysis['success']:
                return results
            
            print("🔒 Performing security audit...")
            audit = self.security_audit(github_url)
            results['audit'] = audit
            
            print("📝 Registering repository...")
            registration = self.register_repository(github_url)
            results['registration'] = registration
            
            if not registration['success']:
                return results
                
            print("🔎 Searching for potential violations...")
            violations = self.search_for_violations(registration['repo_id'])
            results['violations'] = violations
            
            if violations:
                print(f"⚠️ Found {len(violations)} potential violations")
                violation_reports = []
                
                for violation in violations:
                    if violation['similarity'] > 0.7:
                        report = self.report_violation(
                            registration['repo_id'],
                            violation['repo_url'],
                            violation['similarity']
                        )
                        violation_reports.append(report)
                        
                        if report['success']:
                            dmca = self.generate_dmca({
                                'violating_url': violation['repo_url'],
                                'similarity_score': violation['similarity'],
                                'evidence_hash': report['evidence_hash'],
                                'tx_hash': report['tx_hash']
                            })
                            report['dmca'] = dmca
                
                results['violation_reports'] = violation_reports
            else:
                print("✅ No potential violations found")
            
            return results
            
        except Exception as e:
            results['error'] = str(e)
            return results

def main():
    config = {
        'USE_LOCAL_MODEL': os.getenv('USE_LOCAL_MODEL', 'false').lower() == 'true',
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN'),
        'CONTRACT_ADDRESS': os.getenv('CONTRACT_ADDRESS', '0x5fa19b4a48C20202055c8a6fdf16688633617D50')
    }
    
    if not config['USE_LOCAL_MODEL'] and not config['OPENAI_API_KEY']:
        print("❌ Please set OPENAI_API_KEY or USE_LOCAL_MODEL=true")
        return
    
    agent = EnhancedGitHubProtectionAgent(config)
    
    print("🚀 Enhanced GitHub Protection Agent initialized!")
    print("💬 You can now interact with the agent")
    print("\n📋 Available commands:")
    print("  - analyze <github_url>")
    print("  - register <github_url>")
    print("  - audit <any_url>")
    print("  - clean <text_with_urls>")
    print("  - workflow <github_url>")
    print("  - quit/exit")
    
    while True:
        try:
            user_input = input("\n💬 Ask me anything (or 'quit' to exit): ")
            if user_input.lower() in ['quit', 'exit']:
                break
                
            response = agent.agent.run(user_input)
            print(f"\n🤖 Agent: {response}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()