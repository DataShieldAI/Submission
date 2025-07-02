import asyncio
import hashlib
import json
import os
import requests
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path

# LangChain imports
from langchain.agents import initialize_agent, AgentType
from langchain.tools import BaseTool, StructuredTool
from langchain.schema import BaseMessage
from langchain.chat_models import ChatAnthropic
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import get_openai_callback

# LlamaIndex imports
from llama_index.core import Document, VectorStoreIndex, ServiceContext
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever

# Web3 and Flow imports
from viem import createWalletClient, http, createPublicClient
import viem
from viem.account import Account

# PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# GitHub API
import git
import tempfile
import shutil

class GitHubProtectionAgent:
    def __init__(self, config: Dict):
        self.config = config
        self.setup_clients()
        self.setup_models()
        self.setup_tools()
        self.setup_agent()
        
    def setup_clients(self):
        """Initialize blockchain and API clients"""
        # Flow EVM client setup
        self.public_client = createPublicClient({
            'transport': http('https://testnet.evm.nodes.onflow.org'),
            'chain': {
                'id': 545,
                'name': 'Flow Testnet'
            }
        })
        
        # Wallet client for transactions
        self.wallet_client = createWalletClient({
            'transport': http('https://testnet.evm.nodes.onflow.org'),
            'chain': {
                'id': 545,
                'name': 'Flow Testnet'
            },
            'account': Account.from_key(self.config['PRIVATE_KEY'])
        })
        
        # GitHub API setup
        self.github_headers = {
            'Authorization': f"token {self.config['GITHUB_TOKEN']}",
            'Accept': 'application/vnd.github.v3+json'
        }
        
    def setup_models(self):
        """Initialize AI models and embeddings"""
        self.llm = ChatAnthropic(
            model="claude-3-5-haiku-20241022",
            api_key=self.config['ANTHROPIC_API_KEY']
        )
        
        # Setup LlamaIndex for code analysis
        self.embed_model = HuggingFaceEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        self.service_context = ServiceContext.from_defaults(
            embed_model=self.embed_model,
            llm=self.llm
        )
        
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
                func=self.generate_dmca,
                name="generate_dmca",
                description="Generate DMCA takedown notice"
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
            max_iterations=10
        )
        
    def analyze_repository(self, github_url: str) -> Dict:
        """Analyze repository and extract key features"""
        try:
            # Clone repository to temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                repo = git.Repo.clone_from(github_url, temp_dir)
                
                # Extract code files
                code_files = []
                for root, dirs, files in os.walk(temp_dir):
                    # Skip .git directory
                    dirs[:] = [d for d in dirs if d != '.git']
                    
                    for file in files:
                        if file.endswith(('.py', '.js', '.java', '.cpp', '.c', '.go', '.rs', '.sol')):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    code_files.append({
                                        'file': file,
                                        'path': file_path.replace(temp_dir, ''),
                                        'content': content[:5000]  # Limit content
                                    })
                            except Exception:
                                continue
                
                # Create documents for LlamaIndex
                documents = []
                for code_file in code_files:
                    doc = Document(
                        text=code_file['content'],
                        metadata={'file': code_file['file'], 'path': code_file['path']}
                    )
                    documents.append(doc)
                
                # Build index and query for key features
                index = VectorStoreIndex.from_documents(
                    documents, 
                    service_context=self.service_context
                )
                
                query_engine = index.as_query_engine()
                
                # Extract key features using AI
                features_query = """
                Identify the key unique features, algorithms, and distinctive code patterns 
                in this repository. Focus on:
                1. Unique algorithms or data structures
                2. Novel implementations
                3. Distinctive code patterns
                4. Key function signatures
                5. Architecture patterns
                Return as a JSON list of strings.
                """
                
                response = query_engine.query(features_query)
                
                # Generate repository hash
                repo_content = "".join([f['content'] for f in code_files])
                repo_hash = hashlib.sha256(repo_content.encode()).hexdigest()
                
                # Generate fingerprint using key features
                fingerprint_data = {
                    'total_files': len(code_files),
                    'file_types': list(set([f['file'].split('.')[-1] for f in code_files])),
                    'key_features': str(response),
                    'repo_hash': repo_hash
                }
                
                fingerprint = hashlib.sha256(
                    json.dumps(fingerprint_data, sort_keys=True).encode()
                ).hexdigest()
                
                return {
                    'success': True,
                    'repo_hash': repo_hash,
                    'fingerprint': fingerprint,
                    'key_features': str(response),
                    'total_files': len(code_files),
                    'analysis': fingerprint_data
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def register_repository(self, github_url: str, license_type: str = "MIT") -> Dict:
        """Register repository on blockchain"""
        try:
            # First analyze the repository
            analysis = self.analyze_repository(github_url)
            if not analysis['success']:
                return analysis
            
            # Prepare contract call
            contract_address = self.config['CONTRACT_ADDRESS']
            
            # Call registerRepository function
            tx_hash = self.wallet_client.write_contract(
                address=contract_address,
                abi=self.get_contract_abi(),
                function_name='registerRepository',
                args=[
                    github_url,
                    analysis['repo_hash'],
                    analysis['fingerprint'],
                    analysis['key_features'].split('\n')[:10],  # Limit features
                    license_type,
                    ""  # IPFS metadata (to be implemented)
                ]
            )
            
            return {
                'success': True,
                'tx_hash': tx_hash,
                'repo_hash': analysis['repo_hash'],
                'fingerprint': analysis['fingerprint']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def search_for_violations(self, repo_id: int, key_features: List[str]) -> List[Dict]:
        """Search GitHub for potential code violations"""
        violations = []
        
        try:
            # Search GitHub using key features
            for feature in key_features[:5]:  # Limit searches
                search_query = f"{feature} language:python OR language:javascript"
                
                response = requests.get(
                    'https://api.github.com/search/code',
                    headers=self.github_headers,
                    params={
                        'q': search_query,
                        'per_page': 10
                    }
                )
                
                if response.status_code == 200:
                    results = response.json()
                    
                    for item in results.get('items', []):
                        # Download and analyze the file
                        file_response = requests.get(
                            item['download_url'], 
                            headers=self.github_headers
                        )
                        
                        if file_response.status_code == 200:
                            # Calculate similarity (simplified)
                            similarity = self.calculate_similarity(
                                feature, 
                                file_response.text
                            )
                            
                            if similarity > 0.7:  # 70% threshold
                                violations.append({
                                    'repo_url': item['repository']['html_url'],
                                    'file_url': item['html_url'],
                                    'similarity': similarity,
                                    'feature_matched': feature
                                })
                
                time.sleep(1)  # Rate limiting
                
        except Exception as e:
            print(f"Error searching for violations: {e}")
            
        return violations
    
    def calculate_similarity(self, feature: str, code: str) -> float:
        """Calculate similarity between feature and code"""
        # Simplified similarity calculation
        feature_words = set(feature.lower().split())
        code_words = set(code.lower().split())
        
        if not feature_words:
            return 0.0
            
        intersection = feature_words.intersection(code_words)
        return len(intersection) / len(feature_words)
    
    def generate_license(self, repo_type: str, usage_requirements: str) -> str:
        """Generate appropriate license based on repository analysis"""
        prompt = f"""
        Generate an appropriate open source license for a {repo_type} repository 
        with the following usage requirements: {usage_requirements}
        
        Consider:
        - Commercial use restrictions if needed
        - Attribution requirements
        - Copyleft vs permissive licensing
        - AI training restrictions
        
        Provide the full license text.
        """
        
        response = self.llm.invoke(prompt)
        return response.content
    
    def security_audit(self, github_url: str) -> Dict:
        """Perform security audit on repository"""
        try:
            analysis = self.analyze_repository(github_url)
            if not analysis['success']:
                return analysis
                
            audit_prompt = f"""
            Perform a security audit on this code repository.
            
            Key features: {analysis['key_features']}
            
            Check for:
            1. Common security vulnerabilities
            2. Hardcoded secrets or keys
            3. Input validation issues
            4. Authentication/authorization flaws
            5. Dependency vulnerabilities
            
            Provide a JSON response with:
            - severity: high/medium/low
            - issues: list of security issues found
            - recommendations: list of fixes
            """
            
            response = self.llm.invoke(audit_prompt)
            
            return {
                'success': True,
                'audit_result': response.content,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def report_violation(self, original_repo_id: int, violating_url: str, similarity_score: float) -> Dict:
        """Report violation to blockchain"""
        try:
            contract_address = self.config['CONTRACT_ADDRESS']
            
            # Generate evidence hash
            evidence = {
                'violating_url': violating_url,
                'similarity_score': similarity_score,
                'reported_at': datetime.now().isoformat()
            }
            evidence_hash = hashlib.sha256(
                json.dumps(evidence, sort_keys=True).encode()
            ).hexdigest()
            
            # Call reportViolation function
            tx_hash = self.wallet_client.write_contract(
                address=contract_address,
                abi=self.get_contract_abi(),
                function_name='reportViolation',
                args=[
                    original_repo_id,
                    violating_url,
                    evidence_hash,
                    int(similarity_score * 100)  # Convert to integer percentage
                ]
            )
            
            return {
                'success': True,
                'tx_hash': tx_hash,
                'evidence_hash': evidence_hash
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_dmca(self, violation_data: Dict) -> str:
        """Generate DMCA takedown notice"""
        try:
            doc = SimpleDocTemplate(
                f"dmca_notice_{int(time.time())}.pdf",
                pagesize=letter
            )
            
            styles = getSampleStyleSheet()
            story = []
            
            # DMCA Notice content
            title = Paragraph("DMCA Takedown Notice", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))
            
            content = f"""
            To Whom It May Concern:
            
            This is a formal DMCA takedown notice for copyrighted code found at:
            {violation_data['violating_url']}
            
            Original Repository: {violation_data.get('original_repo', 'N/A')}
            Similarity Score: {violation_data.get('similarity_score', 0):.2f}%
            
            The infringing content violates copyright protections and should be removed.
            
            Evidence Hash: {violation_data.get('evidence_hash', 'N/A')}
            Blockchain Transaction: {violation_data.get('tx_hash', 'N/A')}
            
            Contact Information:
            Generated by GitHub Protection Agent
            Timestamp: {datetime.now().isoformat()}
            
            This notice is generated automatically based on code similarity analysis.
            """
            
            body = Paragraph(content, styles['Normal'])
            story.append(body)
            
            doc.build(story)
            
            return f"DMCA notice generated successfully for {violation_data['violating_url']}"
            
        except Exception as e:
            return f"Error generating DMCA: {str(e)}"
    
    def get_contract_abi(self) -> List[Dict]:
        """Return contract ABI"""
        # Simplified ABI - in production, load from file
        return [
            {
                "inputs": [
                    {"type": "string", "name": "githubUrl"},
                    {"type": "string", "name": "repoHash"},
                    {"type": "string", "name": "codeFingerprint"},
                    {"type": "string[]", "name": "keyFeatures"},
                    {"type": "string", "name": "licenseType"},
                    {"type": "string", "name": "ipfsMetadata"}
                ],
                "name": "registerRepository",
                "outputs": [{"type": "uint256"}],
                "type": "function"
            },
            {
                "inputs": [
                    {"type": "uint256", "name": "originalRepoId"},
                    {"type": "string", "name": "violatingUrl"},
                    {"type": "string", "name": "evidenceHash"},
                    {"type": "uint256", "name": "similarityScore"}
                ],
                "name": "reportViolation",
                "outputs": [{"type": "uint256"}],
                "type": "function"
            }
        ]
    
    def run_protection_workflow(self, github_url: str) -> Dict:
        """Run complete protection workflow"""
        results = {}
        
        try:
            # Step 1: Analyze repository
            print("🔍 Analyzing repository...")
            analysis = self.analyze_repository(github_url)
            results['analysis'] = analysis
            
            if not analysis['success']:
                return results
            
            # Step 2: Security audit
            print("🔒 Performing security audit...")
            audit = self.security_audit(github_url)
            results['audit'] = audit
            
            # Step 3: Register repository
            print("📝 Registering repository on blockchain...")
            registration = self.register_repository(github_url)
            results['registration'] = registration
            
            if not registration['success']:
                return results
                
            # Step 4: Search for violations
            print("🔎 Searching for potential violations...")
            violations = self.search_for_violations(
                1,  # Assuming repo ID 1 for demo
                analysis['key_features'].split('\n')[:5]
            )
            results['violations'] = violations
            
            # Step 5: Report violations if found
            if violations:
                print(f"⚠️ Found {len(violations)} potential violations")
                violation_reports = []
                
                for violation in violations:
                    if violation['similarity'] > 0.8:  # High similarity threshold
                        report = self.report_violation(
                            1,  # Repo ID
                            violation['repo_url'],
                            violation['similarity']
                        )
                        violation_reports.append(report)
                        
                        # Generate DMCA if violation reported successfully
                        if report['success']:
                            dmca = self.generate_dmca({
                                'violating_url': violation['repo_url'],
                                'similarity_score': violation['similarity'],
                                'evidence_hash': report['evidence_hash'],
                                'tx_hash': report['tx_hash']
                            })
                            report['dmca'] = dmca
                
                results['violation_reports'] = violation_reports
            
            return results
            
        except Exception as e:
            results['error'] = str(e)
            return results

# Main execution
async def main():
    config = {
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN'),
        'PRIVATE_KEY': os.getenv('PRIVATE_KEY'),
        'CONTRACT_ADDRESS': os.getenv('CONTRACT_ADDRESS')
    }
    
    agent = GitHubProtectionAgent(config)
    
    # Example usage
    github_url = "https://github.com/example/repo"
    
    print("🚀 Starting GitHub Protection Agent...")
    results = agent.run_protection_workflow(github_url)
    
    print("\n📊 Results:")
    print(json.dumps(results, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())