"""
Core Enhanced GitHub Protection Agent
"""
import os
from typing import Dict, List
from datetime import datetime
import hashlib
import json

from langchain.agents import initialize_agent, AgentType
from langchain.tools import StructuredTool
from langchain_community.chat_models import ChatOpenAI
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
from .utils import setup_logging

logger = setup_logging(__name__)


class EnhancedGitHubProtectionAgent:
    """Main agent class that coordinates all protection activities"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.setup_models()
        
        # Initialize components
        self.repo_analyzer = RepositoryAnalyzer(config)
        self.security_scanner = SecurityScanner(config, self.llm)
        self.url_processor = URLProcessor(self.llm)
        self.violation_detector = ViolationDetector(config, self.llm)
        self.report_generator = ReportGenerator()
        
        # In-memory storage
        self.repositories = {}
        self.violations = {}
        self.security_audits = {}
        self.jobs = {}
        
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
    
    # ===== CORE METHODS =====
    
    def analyze_repository(self, github_url: str) -> Dict:
        """Analyze repository and extract key features"""
        return self.repo_analyzer.analyze_repository(github_url, self.llm)
    
    def register_repository(self, github_url: str, license_type: str = "MIT") -> Dict:
        """Register repository on blockchain"""
        try:
            analysis = self.analyze_repository(github_url)
            if not analysis['success']:
                return analysis
            
            # Simulate blockchain transaction
            import time
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
            
            logger.info(f"📝 Repository registered with ID: {repo_id}")
            
            return {
                'success': True,
                'repo_id': repo_id,
                'tx_hash': tx_hash,
                'repo_hash': analysis['repo_hash'],
                'fingerprint': analysis['fingerprint']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def comprehensive_security_audit(self, input_url: str) -> Dict:
        """Enhanced comprehensive security audit with multi-platform support"""
        try:
            logger.info("🔍 Starting comprehensive security audit...")
            
            # Clean and categorize URL
            url_analysis = self.url_processor.analyze_and_clean_url(input_url)
            
            if not url_analysis['valid']:
                return {
                    'success': False,
                    'error': f"Invalid URL: {url_analysis['error']}",
                    'url_analysis': url_analysis
                }
            
            # Perform security audit
            audit_result = self.security_scanner.comprehensive_audit(
                url_analysis,
                audit_id=len(self.security_audits) + 1
            )
            
            # Generate PDF report if findings exist
            if audit_result['total_findings'] > 0:
                pdf_path = self.report_generator.generate_security_pdf(audit_result)
                audit_result['pdf_report'] = pdf_path
            
            # Store the audit
            self.security_audits[audit_result['audit_id']] = audit_result
            
            return {
                'success': True,
                'audit_id': audit_result['audit_id'],
                **audit_result
            }
            
        except Exception as e:
            logger.error(f"Security audit failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def clean_github_urls(self, url_text: str) -> Dict:
        """Clean and standardize GitHub URLs from text input"""
        return self.url_processor.clean_github_urls(url_text)
    
    def search_for_violations(self, repo_id: int, key_features: List[str] = None) -> List[Dict]:
        """Search GitHub for potential code violations"""
        if repo_id not in self.repositories:
            return []
        
        repo = self.repositories[repo_id]
        return self.violation_detector.search_for_violations(
            repo, 
            key_features
        )
    
    def report_violation(self, original_repo_id: int, violating_url: str, similarity_score: float) -> Dict:
        """Report violation"""
        return self.violation_detector.report_violation(
            original_repo_id,
            violating_url,
            similarity_score,
            self.violations
        )
    
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
    
    def generate_dmca(self, violation_data: Dict) -> str:
        """Generate DMCA takedown notice"""
        return self.violation_detector.generate_dmca(violation_data)
    
    def run_protection_workflow(self, github_url: str) -> Dict:
        """Run complete protection workflow"""
        results = {}
        
        try:
            logger.info("🔍 Analyzing repository...")
            analysis = self.analyze_repository(github_url)
            results['analysis'] = analysis
            
            if not analysis['success']:
                return results
            
            logger.info("🔒 Performing security audit...")
            audit = self.security_audit(github_url)
            results['audit'] = audit
            
            logger.info("📝 Registering repository...")
            registration = self.register_repository(github_url)
            results['registration'] = registration
            
            if not registration['success']:
                return results
                
            logger.info("🔎 Searching for potential violations...")
            violations = self.search_for_violations(registration['repo_id'])
            results['violations'] = violations
            
            if violations:
                logger.info(f"⚠️ Found {len(violations)} potential violations")
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
                logger.info("✅ No potential violations found")
            
            return results
            
        except Exception as e:
            results['error'] = str(e)
            return results