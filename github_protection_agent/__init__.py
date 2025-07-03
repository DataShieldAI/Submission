"""
Enhanced GitHub Protection Agent Package
"""
from .agent_core import EnhancedGitHubProtectionAgent
from .repository_analyzer import RepositoryAnalyzer
from .security_scanner import SecurityScanner
from .url_processor import URLProcessor
from .violation_detector import ViolationDetector
from .report_generator import ReportGenerator
from .secret_patterns import SecretPatterns
from .utils import setup_logging, calculate_security_score

__version__ = "3.0.0"
__all__ = [
    "EnhancedGitHubProtectionAgent",
    "RepositoryAnalyzer",
    "SecurityScanner",
    "URLProcessor",
    "ViolationDetector",
    "ReportGenerator",
    "SecretPatterns",
    "setup_logging",
    "calculate_security_score"
]