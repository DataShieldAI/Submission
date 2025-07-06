"""
Violation Detection Module
Handles searching for code violations and generating DMCA notices
"""
import time
import requests
import hashlib
import json
from typing import Dict, List
from datetime import datetime

from .utils import setup_logging

logger = setup_logging(__name__)


class ViolationDetector:
    """Handles violation detection and reporting"""
    
    def __init__(self, config: Dict, llm):
        self.config = config
        self.llm = llm
        self.github_token = config.get('GITHUB_TOKEN')
    
    def search_for_violations(self, repo: Dict, key_features: List[str] = None) -> List[Dict]:
        """Search GitHub for potential code violations"""
        violations = []
        
        try:
            if not key_features:
                key_features = repo['key_features'].split('\n')[:3]
            
            headers = {}
            if self.github_token:
                headers['Authorization'] = f"token {self.github_token}"
            
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
            logger.error(f"Error searching for violations: {e}")
            
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
    
    def report_violation(self, original_repo_id: int, violating_url: str, 
                        similarity_score: float, violations_storage: Dict) -> Dict:
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
            
            violation_id = len(violations_storage) + 1
            violations_storage[violation_id] = {
                'id': violation_id,
                'original_repo_id': original_repo_id,
                'violating_url': violating_url,
                'similarity_score': similarity_score,
                'evidence_hash': evidence_hash,
                'tx_hash': tx_hash,
                'reported_at': datetime.now().isoformat(),
                'status': 'pending'
            }
            
            logger.info(f"⚠️ Violation reported with ID: {violation_id}")
            
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
    
    def analyze_code_similarity(self, repo1_url: str, repo2_url: str) -> Dict:
        """Perform deep code similarity analysis between two repositories"""
        try:
            analysis_prompt = f"""
            Analyze code similarity between these repositories:
            Repository 1: {repo1_url}
            Repository 2: {repo2_url}
            
            Consider:
            1. Structural similarity
            2. Naming conventions
            3. Algorithm patterns
            4. Unique implementation details
            
            Provide a similarity score (0-1) and explanation.
            """
            
            response = self.llm.invoke(analysis_prompt)
            return {
                'success': True,
                'analysis': response.content
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }