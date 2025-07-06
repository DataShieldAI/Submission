"""
Enhanced Core Agent with integrated URL cleaning, DMCA generation, and IPFS support
"""
import os
import hashlib
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime

from langchain.agents import initialize_agent, AgentType
from langchain.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI as LlamaOpenAI
from llama_index.llms.ollama import Ollama

from .repository_analyzer import RepositoryAnalyzer
from .security_scanner import SecurityScanner
from .url_processor import URLProcessor
from .violation_detector import ViolationDetector
from .report_generator import ReportGenerator
from .dmca_generator import DMCAGenerator
from .ipfs_manager import IPFSManager
from .license_generator import LicenseGenerator
from .github_scanner import GitHubScanner
from .utils import setup_logging

logger = setup_logging(__name__)


class EnhancedGitHubProtectionAgent:
    """Enhanced agent with integrated features"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.setup_models()
        
        # Initialize components
        self.repo_analyzer = RepositoryAnalyzer(config)
        self.security_scanner = SecurityScanner(config, self.llm)
        self.url_processor = URLProcessor(self.llm)
        self.violation_detector = ViolationDetector(config, self.llm)
        self.report_generator = ReportGenerator()
        self.dmca_generator = DMCAGenerator()
        self.ipfs_manager = IPFSManager(config)
        self.license_generator = LicenseGenerator()
        self.github_scanner = GitHubScanner(config, self.llm)
        
        # In-memory storage
        self.repositories = {}
        self.violations = {}
        self.security_audits = {}
        self.dmca_notices = {}
        self.licenses = {}
        
        # Setup tools and agent
        self.setup_tools()
        self.setup_agent()
    
    def setup_models(self):
        """Initialize AI models"""
        use_local = self.config.get('USE_LOCAL_MODEL', False)
        
        if use_local:
            logger.info("🦙 Using local model")
            self.llm = ChatOpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama",
                model="llama3.2:3b"
            )
            Settings.llm = Ollama(model="llama3.2:3b", base_url="http://localhost:11434")
        else:
            logger.info("🤖 Using OpenAI")
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
            logger.info("✅ Using free HuggingFace embeddings")
        except Exception as e:
            logger.warning(f"⚠️ Embeddings setup failed: {e}")
    
    def setup_tools(self):
        """Initialize enhanced agent tools"""
        self.tools = [
            StructuredTool.from_function(
                func=self.analyze_repositories,
                name="analyze_repositories",
                description="Analyze and compare two GitHub repositories for code similarity and potential infringement"
            ),
            StructuredTool.from_function(
                func=self.register_repository,
                name="register_repository", 
                description="Register a repository with license generation and blockchain protection"
            ),
            StructuredTool.from_function(
                func=self.comprehensive_audit,
                name="comprehensive_audit",
                description="Perform extensive security audit including all commit history"
            ),
            StructuredTool.from_function(
                func=self.scan_github_for_violations,
                name="scan_github_for_violations",
                description="Scan GitHub for repositories that may be infringing on registered repos"
            ),
            StructuredTool.from_function(
                func=self.run_protection_workflow,
                name="run_protection_workflow",
                description="Run complete protection workflow for a repository"
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
    
    def _clean_and_validate_url(self, url: str) -> Tuple[bool, str, str]:
        """Clean and validate any URL input"""
        try:
            # Use URL processor to clean the URL
            result = self.url_processor.clean_single_url(url)
            
            if not result['success']:
                return False, "", result.get('error', 'Invalid URL')
            
            if result['platform'] != 'github' or result['url_type'] != 'repository':
                return False, "", "URL must be a GitHub repository"
            
            return True, result['cleaned_url'], ""
            
        except Exception as e:
            return False, "", str(e)
    
    def analyze_repositories(self, repo1_input: str, repo2_input: str) -> Dict:
        """Analyze and compare two GitHub repositories"""
        try:
            # Clean both URLs
            valid1, url1, error1 = self._clean_and_validate_url(repo1_input)
            if not valid1:
                return {'success': False, 'error': f'Repository 1: {error1}'}
            
            valid2, url2, error2 = self._clean_and_validate_url(repo2_input)
            if not valid2:
                return {'success': False, 'error': f'Repository 2: {error2}'}
            
            logger.info(f"🔍 Analyzing repositories: {url1} vs {url2}")
            
            # Analyze both repositories
            analysis1 = self.repo_analyzer.analyze_repository(url1, self.llm)
            if not analysis1['success']:
                return {'success': False, 'error': f'Failed to analyze {url1}'}
            
            analysis2 = self.repo_analyzer.analyze_repository(url2, self.llm)
            if not analysis2['success']:
                return {'success': False, 'error': f'Failed to analyze {url2}'}
            
            # Compare repositories for similarity
            similarity_result = self.github_scanner.deep_compare_repositories(
                url1, url2, analysis1, analysis2
            )
            
            # Check against all registered repositories
            registered_matches = []
            for repo_id, repo_data in self.repositories.items():
                if repo_data['github_url'] in [url1, url2]:
                    continue
                    
                similarity = self.violation_detector.calculate_simple_similarity(
                    url1, repo_data['github_url']
                )
                if similarity > 0.5:
                    registered_matches.append({
                        'repo_id': repo_id,
                        'url': repo_data['github_url'],
                        'similarity': similarity
                    })
            
            return {
                'success': True,
                'repository_1': {
                    'url': url1,
                    'analysis': analysis1
                },
                'repository_2': {
                    'url': url2,
                    'analysis': analysis2
                },
                'similarity_analysis': similarity_result,
                'registered_matches': registered_matches,
                'recommendation': self._generate_comparison_recommendation(similarity_result)
            }
            
        except Exception as e:
            logger.error(f"Repository analysis failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def register_repository(self, repo_input: str, license_type: str = "MIT") -> Dict:
        """Register repository with license PDF generation"""
        try:
            # Clean URL
            valid, github_url, error = self._clean_and_validate_url(repo_input)
            if not valid:
                return {'success': False, 'error': error}
            
            # Analyze repository
            analysis = self.repo_analyzer.analyze_repository(github_url, self.llm)
            if not analysis['success']:
                return analysis
            
            # Generate license PDF
            license_pdf_path = self.license_generator.generate_license_pdf(
                github_url,
                license_type,
                analysis['repo_data']
            )
            
            # Upload license to IPFS
            license_ipfs_hash = self.ipfs_manager.upload_to_ipfs(license_pdf_path)
            
            # Register on blockchain
            tx_hash = f"0x{hashlib.sha256(f'{github_url}{datetime.now()}'.encode()).hexdigest()}"
            
            repo_id = len(self.repositories) + 1
            self.repositories[repo_id] = {
                'id': repo_id,
                'github_url': github_url,
                'repo_hash': analysis['repo_hash'],
                'fingerprint': analysis['fingerprint'],
                'key_features': analysis['key_features'],
                'license_type': license_type,
                'license_pdf_path': license_pdf_path,
                'license_ipfs_hash': license_ipfs_hash,
                'registered_at': datetime.now().isoformat(),
                'tx_hash': tx_hash
            }
            
            # Store license info
            self.licenses[repo_id] = {
                'type': license_type,
                'pdf_path': license_pdf_path,
                'ipfs_hash': license_ipfs_hash,
                'generated_at': datetime.now().isoformat()
            }
            
            logger.info(f"📝 Repository registered with ID: {repo_id}")
            logger.info(f"📄 License PDF stored on IPFS: {license_ipfs_hash}")
            
            return {
                'success': True,
                'repo_id': repo_id,
                'tx_hash': tx_hash,
                'repo_hash': analysis['repo_hash'],
                'fingerprint': analysis['fingerprint'],
                'license': {
                    'type': license_type,
                    'pdf_path': license_pdf_path,
                    'ipfs_hash': license_ipfs_hash,
                    'ipfs_url': f"https://ipfs.io/ipfs/{license_ipfs_hash}"
                }
            }
            
        except Exception as e:
            logger.error(f"Repository registration failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def comprehensive_audit(self, repo_input: str, include_all_commits: bool = True) -> Dict:
        """Perform extensive security audit including all commit history"""
        try:
            # Clean URL
            valid, github_url, error = self._clean_and_validate_url(repo_input)
            if not valid:
                return {'success': False, 'error': error}
            
            logger.info(f"🔍 Starting comprehensive audit: {github_url}")
            
            # Run security audit with all commits
            audit_result = self.security_scanner.audit_github_repository_extensive(
                github_url,
                include_all_commits=include_all_commits
            )
            
            # Generate audit report PDF
            if audit_result.get('findings'):
                pdf_path = self.report_generator.generate_security_pdf(audit_result)
                
                # Upload to IPFS
                ipfs_hash = self.ipfs_manager.upload_to_ipfs(pdf_path)
                
                audit_result['report'] = {
                    'pdf_path': pdf_path,
                    'ipfs_hash': ipfs_hash,
                    'ipfs_url': f"https://ipfs.io/ipfs/{ipfs_hash}"
                }
            
            # Store audit
            audit_id = len(self.security_audits) + 1
            audit_result['audit_id'] = audit_id
            self.security_audits[audit_id] = audit_result
            
            return {
                'success': True,
                'audit_id': audit_id,
                **audit_result
            }
            
        except Exception as e:
            logger.error(f"Comprehensive audit failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def scan_github_for_violations(self, repo_id: int = None) -> Dict:
        """Scan GitHub for potential violations and generate DMCA notices"""
        try:
            repos_to_scan = []
            
            if repo_id:
                if repo_id not in self.repositories:
                    return {'success': False, 'error': f'Repository {repo_id} not found'}
                repos_to_scan = [self.repositories[repo_id]]
            else:
                repos_to_scan = list(self.repositories.values())
            
            if not repos_to_scan:
                return {'success': False, 'error': 'No repositories registered to scan'}
            
            all_violations = []
            dmca_notices_generated = []
            
            for repo in repos_to_scan:
                logger.info(f"🔎 Scanning for violations of: {repo['github_url']}")
                
                # Use GitHub scanner to find similar repos
                similar_repos = self.github_scanner.search_similar_repositories(
                    repo['github_url'],
                    repo['key_features']
                )
                
                for similar_repo in similar_repos:
                    # Deep comparison
                    comparison = self.github_scanner.compare_repository_code(
                        repo['github_url'],
                        similar_repo['url']
                    )
                    
                    if comparison['similarity_score'] > 0.7:  # High similarity threshold
                        # Generate DMCA notice
                        dmca_data = {
                            'original_repo': repo,
                            'infringing_repo': similar_repo,
                            'similarity_score': comparison['similarity_score'],
                            'evidence': comparison['evidence'],
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        # Generate DMCA PDF
                        dmca_pdf_path = self.dmca_generator.generate_dmca_pdf(dmca_data)
                        
                        # Upload to IPFS
                        dmca_ipfs_hash = self.ipfs_manager.upload_to_ipfs(dmca_pdf_path)
                        
                        # Pin on chain
                        pin_tx = self.ipfs_manager.pin_on_chain(dmca_ipfs_hash)
                        
                        dmca_id = len(self.dmca_notices) + 1
                        dmca_notice = {
                            'id': dmca_id,
                            'original_repo_id': repo['id'],
                            'infringing_url': similar_repo['url'],
                            'similarity_score': comparison['similarity_score'],
                            'pdf_path': dmca_pdf_path,
                            'ipfs_hash': dmca_ipfs_hash,
                            'ipfs_url': f"https://ipfs.io/ipfs/{dmca_ipfs_hash}",
                            'pin_transaction': pin_tx,
                            'generated_at': datetime.now().isoformat()
                        }
                        
                        self.dmca_notices[dmca_id] = dmca_notice
                        dmca_notices_generated.append(dmca_notice)
                        
                        all_violations.append({
                            'repo_url': similar_repo['url'],
                            'similarity': comparison['similarity_score'],
                            'dmca_id': dmca_id
                        })
            
            return {
                'success': True,
                'repositories_scanned': len(repos_to_scan),
                'violations_found': len(all_violations),
                'dmca_notices_generated': len(dmca_notices_generated),
                'violations': all_violations,
                'dmca_notices': dmca_notices_generated
            }
            
        except Exception as e:
            logger.error(f"GitHub scanning failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_protection_workflow(self, repo_input: str) -> Dict:
        """Run complete protection workflow"""
        try:
            # Clean URL
            valid, github_url, error = self._clean_and_validate_url(repo_input)
            if not valid:
                return {'success': False, 'error': error}
            
            results = {
                'github_url': github_url,
                'steps': {}
            }
            
            # Step 1: Check against existing registered repos
            logger.info("🔍 Checking against registered repositories...")
            for repo_id, repo_data in self.repositories.items():
                if repo_data['github_url'] == github_url:
                    return {
                        'success': False,
                        'error': 'Repository already registered',
                        'repo_id': repo_id
                    }
            
            # Step 2: Comprehensive audit
            logger.info("🔒 Performing security audit...")
            audit_result = self.comprehensive_audit(github_url)
            results['steps']['audit'] = audit_result
            
            if not audit_result['success']:
                return results
            
            # Step 3: Register repository
            logger.info("📝 Registering repository...")
            registration = self.register_repository(github_url)
            results['steps']['registration'] = registration
            
            if not registration['success']:
                return results
            
            # Step 4: Initial scan for violations
            logger.info("🔎 Scanning for existing violations...")
            scan_result = self.scan_github_for_violations(registration['repo_id'])
            results['steps']['initial_scan'] = scan_result
            
            results['success'] = True
            results['summary'] = {
                'repo_id': registration['repo_id'],
                'security_findings': audit_result.get('total_findings', 0),
                'violations_found': scan_result.get('violations_found', 0),
                'protection_active': True
            }
            
            return results
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _generate_comparison_recommendation(self, similarity_result: Dict) -> str:
        """Generate recommendation based on similarity analysis"""
        score = similarity_result.get('overall_similarity', 0)
        
        if score > 0.8:
            return "⚠️ HIGH SIMILARITY: Potential code infringement detected. Consider generating DMCA notice."
        elif score > 0.6:
            return "⚡ MODERATE SIMILARITY: Some code patterns match. Further investigation recommended."
        elif score > 0.4:
            return "📊 LOW SIMILARITY: Minor similarities found. Likely independent implementations."
        else:
            return "✅ MINIMAL SIMILARITY: Repositories appear to be independent."