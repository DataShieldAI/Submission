"""
Enhanced Security Scanner Module
Adds extensive commit history scanning capability
"""
import os
import re
import git
import shutil
import tempfile
import requests
from typing import List, Dict
from datetime import datetime
from urllib.parse import urlparse
from dotenv import load_dotenv
load_dotenv()

from .security_scanner import SecurityScanner
from .utils import setup_logging

logger = setup_logging(__name__)


class EnhancedSecurityScanner(SecurityScanner):
    """Enhanced security scanner with full commit history analysis"""
    
    def audit_github_repository_extensive(self, github_url: str, 
                                        include_all_commits: bool = True) -> Dict:
        """
        Enhanced GitHub repository audit with option to scan ALL commits
        """
        logger.info(f"🔍 Starting extensive GitHub repository audit...")
        logger.info(f"📊 Full commit history scan: {'ENABLED' if include_all_commits else 'DISABLED'}")
        
        path_parts = [p for p in urlparse(github_url).path.split('/') if p]
        if len(path_parts) < 2:
            return {'error': 'Invalid GitHub repository URL'}
        
        owner, repo = path_parts[0], path_parts[1]
        findings = []
        files_scanned = 0
        commits_scanned = 0
        
        try:
            temp_dir = tempfile.mkdtemp()
            repo_path = os.path.join(temp_dir, repo)
            
            logger.info(f"📥 Cloning repository: {github_url}")
            git_repo = git.Repo.clone_from(github_url, repo_path)
            
            # Scan current state
            logger.info("📁 Scanning current repository state...")
            for root, dirs, files in os.walk(repo_path):
                if '.git' in root:
                    continue
                    
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_path)
                    
                    try:
                        if self.is_text_file(file_path):
                            file_findings = self.scan_file_for_secrets(file_path, relative_path)
                            findings.extend(file_findings)
                            files_scanned += 1
                            
                            if files_scanned % 100 == 0:
                                logger.info(f"   Progress: {files_scanned} files scanned...")
                    except Exception as e:
                        logger.warning(f"⚠️ Error scanning {relative_path}: {e}")
            
            # Extensive commit history scan
            if include_all_commits:
                logger.info("🔍 Starting EXTENSIVE commit history scan...")
                commit_findings, commits_scanned = self._scan_all_commits(git_repo, repo_path)
                findings.extend(commit_findings)
            else:
                # Standard commit scan (last 50 commits)
                logger.info("🔍 Scanning recent commit history...")
                commit_findings = self.scan_commit_history_for_secrets(git_repo, repo_path)
                findings.extend(commit_findings)
                commits_scanned = min(50, len(list(git_repo.iter_commits('--all'))))
            
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            return {'error': f'Failed to clone or scan repository: {str(e)}'}
        
        # Categorize findings
        critical_findings = [f for f in findings if f['severity'] == 'critical']
        high_findings = [f for f in findings if f['severity'] == 'high']
        medium_findings = [f for f in findings if f['severity'] == 'medium']
        low_findings = [f for f in findings if f['severity'] == 'low']
        
        # Group findings by type
        findings_by_type = {}
        for finding in findings:
            pattern_name = finding.get('pattern_name', 'unknown')
            if pattern_name not in findings_by_type:
                findings_by_type[pattern_name] = []
            findings_by_type[pattern_name].append(finding)
        
        return {
            'findings': findings,
            'files_scanned': files_scanned,
            'commits_scanned': commits_scanned,
            'total_findings': len(findings),
            'critical_findings': len(critical_findings),
            'high_findings': len(high_findings),
            'medium_findings': len(medium_findings),
            'low_findings': len(low_findings),
            'findings_by_type': findings_by_type,
            'repository_info': {
                'owner': owner,
                'repo': repo,
                'url': github_url
            },
            'scan_type': 'extensive' if include_all_commits else 'standard'
        }
    
    def _scan_all_commits(self, git_repo, repo_path: str) -> tuple:
        """Scan ALL commits in repository history"""
        findings = []
        commits_scanned = 0
        
        try:
            # Get all commits
            all_commits = list(git_repo.iter_commits('--all'))
            total_commits = len(all_commits)
            
            logger.info(f"📊 Total commits to scan: {total_commits}")
            
            # Process in batches for better performance
            batch_size = 100
            
            for i in range(0, total_commits, batch_size):
                batch = all_commits[i:i + batch_size]
                logger.info(f"   Processing commits {i+1} to {min(i+batch_size, total_commits)}...")
                
                for commit in batch:
                    commits_scanned += 1
                    
                    try:
                        # For each commit, check all changes
                        if commit.parents:
                            for parent in commit.parents:
                                diffs = parent.diff(commit, create_patch=True)
                                findings.extend(self._scan_commit_diffs(diffs, commit))
                        else:
                            # First commit - check all files
                            tree_findings = self._scan_initial_commit(commit)
                            findings.extend(tree_findings)
                        
                    except Exception as e:
                        logger.warning(f"Error scanning commit {commit.hexsha[:8]}: {e}")
                        continue
                
                # Log progress
                if commits_scanned % 500 == 0:
                    logger.info(f"   Progress: {commits_scanned}/{total_commits} commits scanned...")
            
            logger.info(f"✅ Completed scanning {commits_scanned} commits")
            
            # Deduplicate findings
            findings = self._deduplicate_findings(findings)
            
        except Exception as e:
            logger.error(f"⚠️ Error during extensive commit scan: {e}")
        
        return findings, commits_scanned
    
    def _scan_commit_diffs(self, diffs, commit) -> List[Dict]:
        """Scan diffs for secrets"""
        findings = []
        
        for diff in diffs:
            try:
                if not diff.diff:
                    continue
                
                patch_text = diff.diff.decode('utf-8', errors='ignore')
                lines = patch_text.split('\n')
                
                for line in lines:
                    # Check both added and removed lines
                    if line.startswith(('+', '-')) and not line.startswith(('+++', '---')):
                        line_content = line[1:]
                        line_type = 'added' if line.startswith('+') else 'removed'
                        
                        for pattern_name, pattern_info in self.secret_patterns.get_patterns().items():
                            matches = re.finditer(pattern_info['pattern'], line_content, re.IGNORECASE)
                            
                            for match in matches:
                                if self.secret_patterns.is_likely_real_secret(match.group(), pattern_name):
                                    findings.append({
                                        'type': 'historical_secret_leak',
                                        'pattern_name': pattern_name,
                                        'file_path': diff.a_path or diff.b_path or 'unknown',
                                        'commit_hash': commit.hexsha[:8],
                                        'commit_date': commit.committed_datetime.isoformat(),
                                        'commit_author': str(commit.author),
                                        'commit_message': commit.message.strip()[:100],
                                        'line_type': line_type,
                                        'line_content': line_content.strip()[:200],
                                        'matched_content': match.group()[:50] + '...' if len(match.group()) > 50 else match.group(),
                                        'severity': pattern_info['severity'],
                                        'description': f"Historical {pattern_info['description']} found in commit history",
                                        'recommendation': f"{pattern_info['recommendation']} Found in git history - {line_type} in commit."
                                    })
            except Exception as e:
                logger.debug(f"Error processing diff: {e}")
                continue
        
        return findings
    
    def _scan_initial_commit(self, commit) -> List[Dict]:
        """Scan the initial commit's files"""
        findings = []
        
        try:
            for item in commit.tree.traverse():
                if item.type == 'blob':  # It's a file
                    try:
                        content = item.data_stream.read().decode('utf-8', errors='ignore')
                        lines = content.split('\n')
                        
                        for line_num, line in enumerate(lines, 1):
                            for pattern_name, pattern_info in self.secret_patterns.get_patterns().items():
                                matches = re.finditer(pattern_info['pattern'], line, re.IGNORECASE)
                                
                                for match in matches:
                                    if self.secret_patterns.is_likely_real_secret(match.group(), pattern_name):
                                        findings.append({
                                            'type': 'historical_secret_leak',
                                            'pattern_name': pattern_name,
                                            'file_path': item.path,
                                            'commit_hash': commit.hexsha[:8],
                                            'commit_date': commit.committed_datetime.isoformat(),
                                            'line_number': line_num,
                                            'line_content': line.strip(),
                                            'matched_content': match.group()[:50] + '...' if len(match.group()) > 50 else match.group(),
                                            'severity': pattern_info['severity'],
                                            'description': f"Historical {pattern_info['description']} in initial commit",
                                            'recommendation': pattern_info['recommendation']
                                        })
                    except:
                        continue
        except Exception as e:
            logger.debug(f"Error scanning initial commit: {e}")
        
        return findings
    
    def _deduplicate_findings(self, findings: List[Dict]) -> List[Dict]:
        """Remove duplicate findings"""
        seen = set()
        unique_findings = []
        
        for finding in findings:
            # Create a unique key for each finding
            key = (
                finding.get('pattern_name'),
                finding.get('file_path'),
                finding.get('matched_content', '')[:20]  # First 20 chars
            )
            
            if key not in seen:
                seen.add(key)
                unique_findings.append(finding)
        
        return unique_findings