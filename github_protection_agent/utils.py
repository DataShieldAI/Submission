"""
Utility Functions Module
Common utilities used across the agent
"""
import logging
import sys
from typing import Any


def setup_logging(name: str) -> logging.Logger:
    """Setup logging configuration"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger


def sanitize_for_display(text: str, max_length: int = 50) -> str:
    """Sanitize text for display"""
    if len(text) > max_length:
        return text[:max_length] + '...'
    return text


def calculate_security_score(findings: dict) -> float:
    """Calculate overall security score based on findings"""
    base_score = 100.0
    
    # Deduct points based on severity
    critical_penalty = findings.get('critical_findings', 0) * 20
    high_penalty = findings.get('high_findings', 0) * 10
    medium_penalty = findings.get('medium_findings', 0) * 5
    low_penalty = findings.get('low_findings', 0) * 2
    
    total_penalty = critical_penalty + high_penalty + medium_penalty + low_penalty
    score = max(0, base_score - total_penalty)
    
    return score