import asyncio
import hashlib
import json
import os
import requests
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

# LangChain imports with OpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import BaseTool, StructuredTool
from langchain.schema import BaseMessage
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

# LlamaIndex imports (simplified)
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI as LlamaOpenAI
from llama_index.llms.ollama import Ollama

# Web3 and Flow imports (simplified)
import requests as web3_requests

# GitHub API
import subprocess

class SimpleGitHubProtectionAgent:
    def __init__(self, config: Dict):
        self.config = config
        self.setup_models()
        self.setup_tools()
        self.setup_agent()
        
        # Simple in-memory storage instead of database
        self.repositories = {}
        self.violations = {}
        self.jobs = {}
        
    def setup_models(self):
        """Initialize AI models"""
        
        # Choose between OpenAI or Ollama
        use_ollama = self.config.get('USE_OLLAMA', False)
        
        if use_ollama:
            print("🦙 Using Ollama (free local model)")
            # LangChain with Ollama
            self.llm = ChatOpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama",  # Required but ignored
                model="llama3.2:3b"  # You can change this model
            )
            
            # LlamaIndex with Ollama
            Settings.llm = Ollama(model="llama3.2:3b", base_url="http://localhost:11434")
            
        else:
            print("🤖 Using OpenAI")
            # LangChain with OpenAI
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",  # Cheaper model
                api_key=self.config['OPENAI_API_KEY']
            )
            
            # LlamaIndex with OpenAI
            Settings.llm = LlamaOpenAI(
                model="gpt-4o-mini",
                api_key=self.config['OPENAI_API_KEY']
            )
        
        # Setup embeddings (free option)
        try:
            Settings.embed_model = HuggingFaceEmbedding(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            print("✅ Using free HuggingFace embeddings")
        except Exception as e:
            print(f"⚠️ Embeddings setup failed: {e}")
            print("💡 Install: pip install sentence-transformers")
        
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
            max_iterations=5  # Reduced for faster responses
        )
        
    def analyze_repository(self, github_url: str) -> Dict:
        """Analyze repository and extract key features (simplified)"""
        try:
            # Simple approach: download repo info via GitHub API
            repo_parts = github_url.replace('https://github.com/', '').split('/')
            if len(repo_parts) < 2:
                return {'success': False, 'error': 'Invalid GitHub URL'}
            
            owner, repo = repo_parts[0], repo_parts[1]
            
            # Get repository info via GitHub API
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
            
            # Get file list (first page)
            contents_response = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}/contents",
                headers=headers
            )
            
            files = []
            if contents_response.status_code == 200:
                contents = contents_response.json()
                files = [item['name'] for item in contents if item['type'] == 'file']
            
            # Simple fingerprinting based on repo metadata
            fingerprint_data = {
                'name': repo_data.get('name', ''),
                'description': repo_data.get('description', ''),
                'language': repo_data.get('language', ''),
                'size': repo_data.get('size', 0),
                'files': files[:10],  # First 10 files
                'created_at': repo_data.get('created_at', ''),
            }
            
            # Generate hash from repository data
            repo_hash = hashlib.sha256(
                json.dumps(fingerprint_data, sort_keys=True).encode()
            ).hexdigest()
            
            # Generate fingerprint
            fingerprint = hashlib.sha256(
                f"{repo_data.get('full_name', '')}{repo_data.get('created_at', '')}".encode()
            ).hexdigest()
            
            # Use AI to extract key features
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
        """Register repository on blockchain (simplified)"""
        try:
            # First analyze the repository
            analysis = self.analyze_repository(github_url)
            if not analysis['success']:
                return analysis
            
            # Simulate blockchain transaction (replace with actual Web3 call)
            contract_address = self.config['CONTRACT_ADDRESS']
            
            # For now, just simulate the transaction
            tx_hash = f"0x{hashlib.sha256(f'{github_url}{time.time()}'.encode()).hexdigest()}"
            
            # Store in memory (replace with actual blockchain call)
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
    
    def search_for_violations(self, repo_id: int, key_features: List[str] = None) -> List[Dict]:
        """Search GitHub for potential code violations (simplified)"""
        violations = []
        
        try:
            if repo_id not in self.repositories:
                return []
            
            repo = self.repositories[repo_id]
            
            # Use key features from registration if not provided
            if not key_features:
                key_features = repo['key_features'].split('\n')[:3]
            
            headers = {}
            if self.config.get('GITHUB_TOKEN'):
                headers['Authorization'] = f"token {self.config['GITHUB_TOKEN']}"
            
            # Search GitHub using repository name and language
            search_terms = [
                repo['github_url'].split('/')[-1],  # repo name
                repo.get('language', 'python')
            ]
            
            for term in search_terms[:2]:  # Limit searches to avoid rate limits
                search_query = f"{term} in:name,description"
                
                response = requests.get(
                    'https://api.github.com/search/repositories',
                    headers=headers,
                    params={
                        'q': search_query,
                        'per_page': 5
                    }
                )
                
                if response.status_code == 200:
                    results = response.json()
                    
                    for item in results.get('items', []):
                        # Skip if it's the same repository
                        if item['html_url'] == repo['github_url']:
                            continue
                        
                        # Simple similarity check (can be enhanced)
                        similarity = self.calculate_simple_similarity(
                            repo['github_url'], 
                            item['html_url']
                        )
                        
                        if similarity > 0.5:  # 50% threshold
                            violations.append({
                                'repo_url': item['html_url'],
                                'similarity': similarity,
                                'name': item['name'],
                                'description': item.get('description', ''),
                                'language': item.get('language', ''),
                                'created_at': item.get('created_at', '')
                            })
                
                time.sleep(1)  # Rate limiting
                
        except Exception as e:
            print(f"Error searching for violations: {e}")
            
        return violations
    
    def calculate_simple_similarity(self, original_url: str, candidate_url: str) -> float:
        """Calculate simple similarity between repositories"""
        # Very basic similarity - can be enhanced with more sophisticated algorithms
        original_name = original_url.split('/')[-1].lower()
        candidate_name = candidate_url.split('/')[-1].lower()
        
        # Check for exact name match
        if original_name == candidate_name:
            return 0.9
        
        # Check for similar names
        common_chars = set(original_name) & set(candidate_name)
        similarity = len(common_chars) / max(len(original_name), len(candidate_name))
        
        return similarity
    
    def generate_license(self, repo_type: str, usage_requirements: str) -> str:
        """Generate appropriate license based on repository analysis"""
        prompt = f"""
        Generate an appropriate open source license for a {repo_type} repository 
        with the following usage requirements: {usage_requirements}
        
        Consider:
        - Commercial use restrictions if needed
        - Attribution requirements
        - AI training restrictions if requested
        
        Provide a concise license recommendation and key points.
        """
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"Error generating license: {e}"
    
    def security_audit(self, github_url: str) -> Dict:
        """Perform security audit on repository (simplified)"""
        try:
            analysis = self.analyze_repository(github_url)
            if not analysis['success']:
                return analysis
                
            audit_prompt = f"""
            Perform a basic security audit on this repository:
            
            Name: {analysis['analysis'].get('name', '')}
            Language: {analysis['analysis'].get('language', '')}
            Description: {analysis['analysis'].get('description', '')}
            Files: {', '.join(analysis['analysis'].get('files', []))}
            
            Identify potential security concerns and recommendations.
            Focus on common vulnerabilities for {analysis['analysis'].get('language', 'this')} projects.
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
        """Report violation (simplified - stores in memory)"""
        try:
            # Generate evidence hash
            evidence = {
                'violating_url': violating_url,
                'similarity_score': similarity_score,
                'reported_at': datetime.now().isoformat()
            }
            evidence_hash = hashlib.sha256(
                json.dumps(evidence, sort_keys=True).encode()
            ).hexdigest()
            
            # Simulate blockchain transaction
            tx_hash = f"0x{hashlib.sha256(f'{violating_url}{time.time()}'.encode()).hexdigest()}"
            
            # Store violation
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
        """Generate DMCA takedown notice (simplified)"""
        try:
            dmca_prompt = f"""
            Generate a professional DMCA takedown notice for the following violation:
            
            Violating URL: {violation_data['violating_url']}
            Similarity Score: {violation_data.get('similarity_score', 0):.2f}
            Evidence Hash: {violation_data.get('evidence_hash', 'N/A')}
            
            Include:
            - Formal legal language
            - Clear identification of copyrighted work
            - Description of infringement
            - Request for removal
            - Contact information placeholder
            """
            
            response = self.llm.invoke(dmca_prompt)
            return response.content
            
        except Exception as e:
            return f"Error generating DMCA: {str(e)}"
    
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
            print("📝 Registering repository...")
            registration = self.register_repository(github_url)
            results['registration'] = registration
            
            if not registration['success']:
                return results
                
            # Step 4: Search for violations
            print("🔎 Searching for potential violations...")
            violations = self.search_for_violations(registration['repo_id'])
            results['violations'] = violations
            
            # Step 5: Report violations if found
            if violations:
                print(f"⚠️ Found {len(violations)} potential violations")
                violation_reports = []
                
                for violation in violations:
                    if violation['similarity'] > 0.7:  # High similarity threshold
                        report = self.report_violation(
                            registration['repo_id'],
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
            else:
                print("✅ No potential violations found")
            
            return results
            
        except Exception as e:
            results['error'] = str(e)
            return results

# Simple test function
def main():
    config = {
        'USE_OLLAMA': os.getenv('USE_OLLAMA', 'false').lower() == 'true',
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN'),
        'CONTRACT_ADDRESS': os.getenv('CONTRACT_ADDRESS', '0x5fa19b4a48C20202055c8a6fdf16688633617D50')
    }
    
    # Check requirements
    if not config['USE_OLLAMA'] and not config['OPENAI_API_KEY']:
        print("❌ Please set OPENAI_API_KEY or USE_OLLAMA=true")
        return
    
    agent = SimpleGitHubProtectionAgent(config)
    
    print("🚀 GitHub Protection Agent initialized!")
    print("💬 You can now interact with the agent")
    
    # Interactive mode
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