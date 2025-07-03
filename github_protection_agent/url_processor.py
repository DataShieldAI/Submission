"""
URL Processing Module
Handles URL cleaning, analysis, and categorization
"""
import re
import json
from typing import List, Dict
from urllib.parse import urlparse, parse_qs

from .utils import setup_logging

logger = setup_logging(__name__)


class URLProcessor:
    """Handles URL processing and cleaning"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def clean_github_urls(self, url_text: str) -> Dict:
        """Clean and standardize GitHub URLs from text input"""
        try:
            logger.info("🧹 Cleaning URLs from text input...")
            
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
            cleaned_url = re.sub(r'^["\'\s\[\]()]+|["\'\s\[\]()]+$', '', cleaned_url)
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
            ai_analysis = self.ai_categorize_url(url)
            
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
    
    def ai_categorize_url(self, url: str) -> Dict:
        """Use AI to categorize URL"""
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
            return json.loads(ai_response.content)
        except:
            # Fallback to manual analysis
            parsed = urlparse(url)
            return self.manual_url_analysis(url, parsed)
    
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