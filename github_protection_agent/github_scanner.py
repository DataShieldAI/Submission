"""
GitHub Scanner Module
Searches GitHub for potentially infringing repositories
"""
import time
import requests
from typing import List, Dict, Set
from difflib import SequenceMatcher
import re
from dotenv import load_dotenv
load_dotenv()

from .utils import setup_logging

logger = setup_logging(__name__)


class GitHubScanner:
    """Handles GitHub repository scanning and comparison"""
    
    def __init__(self, config: Dict, llm):
        self.config = config
        self.llm = llm
        self.github_token = config.get('GITHUB_TOKEN')
        self.headers = {}
        if self.github_token:
            self.headers['Authorization'] = f"token {self.github_token}"
    
    def search_similar_repositories(self, repo_url: str, key_features: str) -> List[Dict]:
        """Search GitHub for repositories similar to the protected one"""
        try:
            # Extract repo info
            repo_parts = repo_url.replace('https://github.com/', '').split('/')
            owner, repo_name = repo_parts[0], repo_parts[1]
            
            # Extract search terms from key features
            search_terms = self._extract_search_terms(key_features, repo_name)
            
            similar_repos = []
            searched_urls = {repo_url}  # Avoid scanning the original
            
            for term in search_terms[:5]:  # Limit searches
                logger.info(f"🔎 Searching GitHub for: {term}")
                
                try:
                    # Search repositories
                    search_url = 'https://api.github.com/search/repositories'
                    params = {
                        'q': term,
                        'sort': 'stars',
                        'order': 'desc',
                        'per_page': 20
                    }
                    
                    response = requests.get(search_url, headers=self.headers, params=params)
                    
                    if response.status_code == 200:
                        results = response.json()
                        
                        for item in results.get('items', []):
                            if item['html_url'] not in searched_urls:
                                searched_urls.add(item['html_url'])
                                
                                # Quick similarity check on name/description
                                name_similarity = self._calculate_text_similarity(
                                    repo_name.lower(),
                                    item['name'].lower()
                                )
                                
                                if name_similarity > 0.3:  # Low threshold for initial scan
                                    similar_repos.append({
                                        'url': item['html_url'],
                                        'name': item['name'],
                                        'description': item.get('description', ''),
                                        'stars': item.get('stargazers_count', 0),
                                        'language': item.get('language', ''),
                                        'created_at': item.get('created_at', ''),
                                        'initial_similarity': name_similarity
                                    })
                    
                    time.sleep(2)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"Search error for term '{term}': {e}")
                    continue
            
            # Sort by initial similarity
            similar_repos.sort(key=lambda x: x['initial_similarity'], reverse=True)
            
            return similar_repos[:20]  # Return top 20 candidates
            
        except Exception as e:
            logger.error(f"GitHub search failed: {e}")
            return []
    
    def deep_compare_repositories(self, repo1_url: str, repo2_url: str, 
                                analysis1: Dict, analysis2: Dict) -> Dict:
        """Perform deep comparison between two repositories"""
        try:
            comparison_result = {
                'file_structure_similarity': 0.0,
                'code_pattern_similarity': 0.0,
                'language_match': False,
                'size_similarity': 0.0,
                'overall_similarity': 0.0,
                'evidence': []
            }
            
            # Compare languages
            lang1 = analysis1.get('repo_data', {}).get('language', '')
            lang2 = analysis2.get('repo_data', {}).get('language', '')
            comparison_result['language_match'] = lang1 == lang2
            
            if comparison_result['language_match']:
                comparison_result['evidence'].append(f"Both repositories use {lang1}")
            
            # Compare file structures
            files1 = set(analysis1.get('analysis', {}).get('files', []))
            files2 = set(analysis2.get('analysis', {}).get('files', []))
            
            if files1 and files2:
                common_files = files1 & files2
                file_similarity = len(common_files) / max(len(files1), len(files2))
                comparison_result['file_structure_similarity'] = file_similarity
                
                if file_similarity > 0.5:
                    comparison_result['evidence'].append(
                        f"High file structure similarity: {file_similarity:.2%}"
                    )
                    comparison_result['evidence'].append(
                        f"Common files: {', '.join(list(common_files)[:5])}"
                    )
            
            # Compare repository sizes
            size1 = analysis1.get('analysis', {}).get('size', 1)
            size2 = analysis2.get('analysis', {}).get('size', 1)
            size_ratio = min(size1, size2) / max(size1, size2)
            comparison_result['size_similarity'] = size_ratio
            
            # Get code samples for comparison
            code_similarity = self.compare_repository_code(repo1_url, repo2_url)
            comparison_result['code_pattern_similarity'] = code_similarity.get('similarity_score', 0)
            comparison_result['evidence'].extend(code_similarity.get('evidence', []))
            
            # Calculate overall similarity
            weights = {
                'file_structure': 0.3,
                'code_pattern': 0.5,
                'language': 0.1,
                'size': 0.1
            }
            
            overall = (
                weights['file_structure'] * comparison_result['file_structure_similarity'] +
                weights['code_pattern'] * comparison_result['code_pattern_similarity'] +
                weights['language'] * (1.0 if comparison_result['language_match'] else 0.0) +
                weights['size'] * comparison_result['size_similarity']
            )
            
            comparison_result['overall_similarity'] = overall
            
            return comparison_result
            
        except Exception as e:
            logger.error(f"Deep comparison failed: {e}")
            return {
                'overall_similarity': 0.0,
                'error': str(e)
            }
    
    def compare_repository_code(self, repo1_url: str, repo2_url: str) -> Dict:
        """Compare actual code content between repositories"""
        try:
            # Get key files from both repos
            files1 = self._get_repository_files(repo1_url)
            files2 = self._get_repository_files(repo2_url)
            
            if not files1 or not files2:
                return {'similarity_score': 0.0, 'evidence': []}
            
            similarities = []
            evidence = []
            
            # Compare main files
            for file1 in files1[:10]:  # Limit to top 10 files
                for file2 in files2[:10]:
                    if file1['name'] == file2['name']:
                        # Get file contents
                        content1 = self._get_file_content(file1['download_url'])
                        content2 = self._get_file_content(file2['download_url'])
                        
                        if content1 and content2:
                            similarity = self._calculate_code_similarity(content1, content2)
                            similarities.append(similarity)
                            
                            if similarity > 0.8:
                                evidence.append(
                                    f"File '{file1['name']}' is {similarity:.2%} similar"
                                )
            
            # Use AI for semantic analysis
            if similarities:
                avg_similarity = sum(similarities) / len(similarities)
                
                # Get AI assessment
                ai_assessment = self._get_ai_code_comparison(
                    repo1_url, repo2_url, evidence
                )
                
                if ai_assessment:
                    evidence.append(f"AI Assessment: {ai_assessment}")
                
                return {
                    'similarity_score': avg_similarity,
                    'evidence': evidence
                }
            
            return {'similarity_score': 0.0, 'evidence': []}
            
        except Exception as e:
            logger.error(f"Code comparison failed: {e}")
            return {'similarity_score': 0.0, 'evidence': [str(e)]}
    
    def _extract_search_terms(self, key_features: str, repo_name: str) -> List[str]:
        """Extract search terms from key features"""
        terms = [repo_name]
        
        # Extract technical terms from features
        technical_terms = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b', key_features)
        terms.extend(technical_terms[:3])
        
        # Extract framework/library names
        common_frameworks = ['react', 'vue', 'angular', 'django', 'flask', 'express', 
                           'spring', 'rails', 'laravel', 'pytorch', 'tensorflow']
        
        features_lower = key_features.lower()
        for framework in common_frameworks:
            if framework in features_lower:
                terms.append(framework)
        
        # Add combinations
        if len(terms) > 1:
            terms.append(f"{terms[0]} {terms[1]}")
        
        return list(dict.fromkeys(terms))  # Remove duplicates
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _get_repository_files(self, repo_url: str) -> List[Dict]:
        """Get list of files from repository"""
        try:
            repo_parts = repo_url.replace('https://github.com/', '').split('/')
            owner, repo = repo_parts[0], repo_parts[1]
            
            url = f"https://api.github.com/repos/{owner}/{repo}/contents"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                contents = response.json()
                # Filter for code files
                code_files = [
                    item for item in contents 
                    if item['type'] == 'file' and 
                    any(item['name'].endswith(ext) for ext in 
                        ['.py', '.js', '.java', '.cpp', '.c', '.go', '.rs', '.ts'])
                ]
                return code_files
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get repository files: {e}")
            return []
    
    def _get_file_content(self, download_url: str) -> str:
        """Get content of a file from GitHub"""
        try:
            response = requests.get(download_url, headers=self.headers)
            if response.status_code == 200:
                return response.text[:10000]  # Limit size
            return ""
        except:
            return ""
    
    def _calculate_code_similarity(self, code1: str, code2: str) -> float:
        """Calculate similarity between code snippets"""
        # Remove comments and whitespace for better comparison
        code1_clean = re.sub(r'#.*$|//.*$|/\*.*?\*/', '', code1, flags=re.MULTILINE)
        code2_clean = re.sub(r'#.*$|//.*$|/\*.*?\*/', '', code2, flags=re.MULTILINE)
        
        # Remove excess whitespace
        code1_clean = ' '.join(code1_clean.split())
        code2_clean = ' '.join(code2_clean.split())
        
        return SequenceMatcher(None, code1_clean, code2_clean).ratio()
    
    def _get_ai_code_comparison(self, repo1_url: str, repo2_url: str, 
                               initial_evidence: List[str]) -> str:
        """Get AI assessment of code similarity"""
        try:
            prompt = f"""
            Analyze the similarity between these two GitHub repositories:
            Repository 1: {repo1_url}
            Repository 2: {repo2_url}
            
            Initial evidence:
            {chr(10).join(initial_evidence)}
            
            Consider:
            1. Code structure and patterns
            2. Algorithm implementation
            3. Unique features or innovations
            4. Whether this appears to be legitimate inspiration vs copying
            
            Provide a brief assessment of similarity and potential infringement.
            """
            
            response = self.llm.invoke(prompt)
            return response.content
            
        except Exception as e:
            logger.error(f"AI comparison failed: {e}")
            return ""