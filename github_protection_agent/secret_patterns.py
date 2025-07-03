"""
Secret Patterns Module
Defines patterns for detecting various types of secrets and credentials
"""
import re
from typing import Dict


class SecretPatterns:
    """Manages patterns for detecting secrets in code"""
    
    def get_patterns(self) -> Dict:
        """Comprehensive patterns for detecting secrets"""
        return {
            'aws_access_key': {
                'pattern': r'AKIA[0-9A-Z]{16}',
                'severity': 'critical',
                'description': 'AWS Access Key ID detected',
                'recommendation': 'Immediately revoke this AWS access key and rotate credentials'
            },
            'aws_secret_key': {
                'pattern': r'aws[_\s]*secret[_\s]*access[_\s]*key[_\s]*[=:]\s*["\']?[A-Za-z0-9/+=]{40}["\']?',
                'severity': 'critical',
                'description': 'AWS Secret Access Key detected',
                'recommendation': 'Immediately revoke this AWS secret key and rotate credentials'
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
            'slack_token': {
                'pattern': r'xox[baprs]-([0-9a-zA-Z]{10,48})',
                'severity': 'high',
                'description': 'Slack token detected',
                'recommendation': 'Revoke this Slack token immediately'
            },
            'discord_token': {
                'pattern': r'[MN][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27}',
                'severity': 'high',
                'description': 'Discord bot token detected',
                'recommendation': 'Regenerate this Discord bot token'
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
            'password_field': {
                'pattern': r'(?i)(password|passwd|pwd)\s*[=:]\s*[\'"]?[^\s\'"]{3,}[\'"]?',
                'severity': 'medium',
                'description': 'Hardcoded password detected',
                'recommendation': 'Use secure password management instead of hardcoding'
            },
            'email_address': {
                'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'severity': 'low',
                'description': 'Email address detected',
                'recommendation': 'Consider if email should be public'
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
            },
            'credit_card': {
                'pattern': r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b',
                'severity': 'critical',
                'description': 'Credit card number pattern detected',
                'recommendation': 'Remove credit card information immediately'
            },
            'google_api_key': {
                'pattern': r'AIza[0-9A-Za-z_-]{35}',
                'severity': 'high',
                'description': 'Google API key detected',
                'recommendation': 'Restrict API key usage and rotate if necessary'
            }
        }
    
    def is_likely_real_secret(self, matched_text: str, pattern_name: str) -> bool:
        """Validate if matched text is likely a real secret"""
        
        # Extract value part if it has assignment
        if any(sep in matched_text for sep in ['=', ':']):
            for sep in ['=', ':']:
                if sep in matched_text:
                    value_part = matched_text.split(sep, 1)[1].strip().strip('\'"')
                    break
        else:
            value_part = matched_text
        
        # Skip common placeholders
        placeholder_patterns = [
            r'^\s*$',  # Empty
            r'^your[_\s]*\w*[_\s]*key',  # your_api_key, your-secret-key, etc.
            r'^insert[_\s]*\w*',  # insert_key_here
            r'^add[_\s]*your',  # add_your_key
            r'^(api|secret|private)[_\s]*key[_\s]*here',
            r'^\$\{.*\}',  # ${API_KEY} environment variable syntax
            r'^<.*>',  # <API_KEY> XML-style placeholder
            r'^\[.*\]',  # [API_KEY] bracket placeholder
            r'^example',  # example_key
            r'^test[_\s]*',  # test_key
            r'^demo[_\s]*',  # demo_key
            r'^dummy[_\s]*',  # dummy_key
            r'^placeholder',
            r'^replace[_\s]*this',
            r'^change[_\s]*me',
            r'^\.\.\.',  # ...
            r'^x+,  # xxx, XXXX
            r'^0+,  # 000, 0000
            r'^1+,  # 111, 1111
            r'^(abc|def|test|sample|demo)123',  # abc123, test123
            r'^sk-[x]{48},  # OpenAI placeholder sk-xxxxxxxx...
            r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12},  # UUID placeholder
        ]
        
        for pattern in placeholder_patterns:
            if re.match(pattern, value_part.lower()):
                return False
        
        # Pattern-specific validation
        if pattern_name == 'aws_access_key':
            # AWS access keys should be exactly 20 characters and start with AKIA
            return len(value_part) == 20 and value_part.startswith('AKIA')
        
        elif pattern_name == 'aws_secret_key':
            # AWS secret keys should be exactly 40 characters
            return len(value_part) == 40
        
        elif pattern_name == 'github_token':
            # GitHub tokens have specific prefixes and lengths
            return (value_part.startswith(('ghp_', 'gho_', 'ghu_', 'ghs_', 'ghr_')) and 
                    len(value_part) >= 40)
        
        elif pattern_name == 'openai_api_key':
            # OpenAI keys start with sk- and are 51 characters total
            return value_part.startswith('sk-') and len(value_part) == 51
        
        elif pattern_name == 'jwt_token':
            # JWT tokens have 3 parts separated by dots
            parts = value_part.split('.')
            return len(parts) == 3 and all(len(part) > 10 for part in parts)
        
        # General entropy check for other patterns
        if len(value_part) >= 16:
            # Check character diversity (entropy)
            unique_chars = len(set(value_part.lower()))
            total_chars = len(value_part)
            diversity_ratio = unique_chars / total_chars
            
            # High diversity suggests real secret
            if diversity_ratio > 0.6:
                return True
        
        # If it's longer than 8 characters and not obviously fake, consider it real
        return len(value_part) > 8