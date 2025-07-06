"""
Repository Analysis Module
Handles GitHub repository analysis and fingerprinting
"""
import hashlib
import json
import requests
from typing import Dict, List
from .utils import setup_logging
from dotenv import load_dotenv
load_dotenv()

logger = setup_logging(__name__)


class RepositoryAnalyzer:
    """Handles repository analysis and fingerprinting"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.github_token = config.get('GITHUB_TOKEN')
    
    def analyze_repository(self, github_url: str, llm) -> Dict:
        """Analyze repository and extract key features"""
        try:
            repo_parts = github_url.replace('https://github.com/', '').split('/')
            if len(repo_parts) < 2:
                return {'success': False, 'error': 'Invalid GitHub URL'}
            
            owner, repo = repo_parts[0], repo_parts[1]
            
            headers = {}
            if self.github_token:
                headers['Authorization'] = f"token {self.github_token}"
            
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
            key_features = self._extract_key_features(repo_data, files, llm)
            
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
            logger.error(f"Repository analysis failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _extract_key_features(self, repo_data: Dict, files: List[str], llm) -> str:
        """Extract key features using AI"""
        features_prompt = f"""
        Analyze this GitHub repository and identify key unique features:
        Name: {repo_data.get('name', '')}
        Description: {repo_data.get('description', '')}
        Language: {repo_data.get('language', '')}
        Files: {', '.join(files[:5])}
        
        List 3-5 distinctive features that make this repository unique.
        """
        
        try:
            response = llm.invoke(features_prompt)
            return response.content
        except Exception as e:
            logger.warning(f"AI feature extraction failed: {e}")
            return f"Language: {repo_data.get('language', 'Unknown')}, Files: {len(files)}"
    
    def get_repository_structure(self, github_url: str) -> Dict:
        """Get detailed repository structure"""
        try:
            repo_parts = github_url.replace('https://github.com/', '').split('/')
            if len(repo_parts) < 2:
                return {'success': False, 'error': 'Invalid GitHub URL'}
            
            owner, repo = repo_parts[0], repo_parts[1]
            
            headers = {}
            if self.github_token:
                headers['Authorization'] = f"token {self.github_token}"
            
            # Get recursive tree
            tree_response = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1",
                headers=headers
            )
            
            if tree_response.status_code != 200:
                # Try master branch
                tree_response = requests.get(
                    f"https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1",
                    headers=headers
                )
            
            if tree_response.status_code == 200:
                tree_data = tree_response.json()
                
                # Organize by file type
                file_types = {}
                for item in tree_data.get('tree', []):
                    if item['type'] == 'blob':
                        ext = item['path'].split('.')[-1] if '.' in item['path'] else 'no_extension'
                        if ext not in file_types:
                            file_types[ext] = []
                        file_types[ext].append(item['path'])
                
                return {
                    'success': True,
                    'total_files': len([i for i in tree_data.get('tree', []) if i['type'] == 'blob']),
                    'file_types': file_types,
                    'tree': tree_data.get('tree', [])
                }
            
            return {'success': False, 'error': 'Failed to retrieve repository structure'}
            
        except Exception as e:
            logger.error(f"Failed to get repository structure: {e}")
            return {'success': False, 'error': str(e)}