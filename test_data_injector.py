# test_data_injector.py - Inject valid test data into your agent

import requests
import time
import json
from datetime import datetime

class TestDataInjector:
    def __init__(self, agent_url: str = "http://localhost:8000"):
        self.agent_url = agent_url
        
    def check_agent_health(self) -> bool:
        """Check if agent is running"""
        try:
            response = requests.get(f"{self.agent_url}/")
            return response.status_code == 200
        except:
            return False
    
    def inject_sample_repositories(self):
        """Inject real, accessible GitHub repositories for testing"""
        print("🌱 Injecting sample repositories...")
        
        # Your custom test repositories
        test_repos = [
            {
                "github_url": "https://github.com/AMRITESH240304/AgentMint",
                "license_type": "MIT",
                "description": "AgentMint - AI agent minting platform"
            },
            {
                "github_url": "https://github.com/ETIM-PAUL/AirClaim",
                "license_type": "MIT", 
                "description": "AirClaim - Airdrop claiming platform"
            },
            {
                "github_url": "https://github.com/Ghost-xDD/BazaarML",
                "license_type": "Apache-2.0",
                "description": "BazaarML - Machine learning marketplace"
            },
            {
                "github_url": "https://github.com/Jeevant010/CrowdStats",
                "license_type": "MIT",
                "description": "CrowdStats - Crowdsourcing statistics platform"
            },
            {
                "github_url": "https://github.com/PhatDot1/Tweet-IP",
                "license_type": "GPL-3.0",
                "description": "Tweet-IP - Twitter intellectual property tracker"
            }
        ]
        
        registered_repos = []
        
        for repo in test_repos:
            try:
                print(f"  📝 Registering {repo['github_url'].split('/')[-1]}...")
                
                response = requests.post(
                    f"{self.agent_url}/register-repository",
                    json=repo,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        repo_id = result.get('repo_id')
                        print(f"     ✅ Registered with ID: {repo_id}")
                        registered_repos.append({**repo, 'repo_id': repo_id})
                    else:
                        print(f"     ❌ Failed: {result.get('error', 'Unknown error')}")
                else:
                    print(f"     ❌ HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"     ❌ Error: {e}")
            
            time.sleep(2)  # Rate limiting
        
        print(f"✅ Successfully registered {len(registered_repos)} repositories")
        return registered_repos
    
    def run_security_audits(self, repositories):
        """Run security audits on the registered repositories"""
        print("🔒 Running security audits...")
        
        audit_results = []
        
        # Run audits on first 3 repos to avoid long wait times
        for repo in repositories[:3]:
            try:
                print(f"  🔍 Auditing {repo['github_url'].split('/')[-1]}...")
                
                response = requests.post(
                    f"{self.agent_url}/security-audit",
                    json={
                        "github_url": repo['github_url'],
                        "audit_type": "comprehensive",
                        "include_private_keys": True,
                        "include_vulnerabilities": True
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        audit_id = result.get('audit_id')
                        findings = result.get('total_findings', 0)
                        print(f"     ✅ Audit ID: {audit_id}, Findings: {findings}")
                        audit_results.append(result)
                    else:
                        print(f"     ❌ Failed: {result.get('error')}")
                else:
                    print(f"     ❌ HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"     ❌ Error: {e}")
            
            time.sleep(3)  # Security audits take time
        
        print(f"✅ Completed {len(audit_results)} security audits")
        return audit_results
    
    def test_url_cleaning(self):
        """Test URL cleaning functionality"""
        print("🧹 Testing URL cleaning...")
        
        test_text = """
        Check out these repos:
        github.com/facebook/react
        https://github.com/microsoft/vscode
        www.github.com/python/cpython
        Also see git@github.com:nodejs/node.git
        """
        
        try:
            response = requests.post(
                f"{self.agent_url}/clean-urls",
                json={"url_text": test_text},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                cleaned_urls = result.get('cleaned_urls', [])
                print(f"     ✅ Found {len(cleaned_urls)} URLs: {cleaned_urls}")
                return result
            else:
                print(f"     ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"     ❌ Error: {e}")
        
        return None
    
    def test_agent_queries(self):
        """Test natural language queries"""
        print("💬 Testing agent queries...")
        
        test_queries = [
            "How many repositories are currently protected?",
            "What security issues were found in the audits?",
            "Show me statistics about the system",
            "What types of violations can you detect?"
        ]
        
        for query in test_queries:
            try:
                print(f"  🤖 Query: {query}")
                
                response = requests.post(
                    f"{self.agent_url}/agent-query",
                    json={"query": query},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        answer = result.get('response', '')[:100]
                        print(f"     ✅ Answer: {answer}...")
                    else:
                        print(f"     ❌ Failed: {result.get('error')}")
                else:
                    print(f"     ❌ HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"     ❌ Error: {e}")
            
            time.sleep(2)
    
    def run_full_workflow_test(self):
        """Test the complete protection workflow"""
        print("🔄 Testing full protection workflow...")
        
        test_repo = {
            "github_url": "https://github.com/AMRITESH240304/AgentMint",
            "license_type": "MIT",
            "description": "AgentMint - AI agent minting platform for testing workflow"
        }
        
        try:
            response = requests.post(
                f"{self.agent_url}/full-protection-workflow",
                json=test_repo,
                timeout=90
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    workflow = result.get('workflow_result', {})
                    print("     ✅ Workflow completed:")
                    print(f"        Analysis: {'✅' if workflow.get('analysis', {}).get('success') else '❌'}")
                    print(f"        Registration: {'✅' if workflow.get('registration', {}).get('success') else '❌'}")
                    print(f"        Security Audit: {'✅' if workflow.get('audit', {}).get('success') else '❌'}")
                    violations = workflow.get('violations', [])
                    print(f"        Violations Found: {len(violations)}")
                    return result
                else:
                    print(f"     ❌ Failed: {result.get('error')}")
            else:
                print(f"     ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"     ❌ Error: {e}")
        
        return None
    
    def show_system_stats(self):
        """Show current system statistics"""
        print("📊 System Statistics:")
        
        try:
            response = requests.get(f"{self.agent_url}/stats")
            if response.status_code == 200:
                stats = response.json()
                print(f"     📁 Repositories: {stats.get('statistics', {}).get('repositories', {}).get('total_tracked', 0)}")
                print(f"     ⚠️ Violations: {stats.get('statistics', {}).get('repositories', {}).get('total_violations', 0)}")
                print(f"     🔒 Security Audits: {stats.get('statistics', {}).get('security_audits', {}).get('total_completed', 0)}")
                print(f"     🛡️ Security Score: {stats.get('statistics', {}).get('security_audits', {}).get('security_score', 'N/A')}")
                return stats
            else:
                print(f"     ❌ HTTP {response.status_code}")
        except Exception as e:
            print(f"     ❌ Error: {e}")
        
        return None
    
    def inject_all_test_data(self):
        """Complete test data injection process"""
        print("🚀 GitHub Protection Agent - Test Data Injection")
        print("="*60)
        
        # Check if agent is running
        if not self.check_agent_health():
            print("❌ Agent is not running! Start it first with:")
            print("   python bootstrap_agent.py")
            return False
        
        print("✅ Agent is running")
        
        try:
            # Step 1: Register repositories
            repositories = self.inject_sample_repositories()
            
            # Step 2: Run security audits
            if repositories:
                audit_results = self.run_security_audits(repositories)
            
            # Step 3: Test URL cleaning
            self.test_url_cleaning()
            
            # Step 4: Test agent queries
            self.test_agent_queries()
            
            # Step 5: Test full workflow
            self.run_full_workflow_test()
            
            # Step 6: Show final stats
            print("\n" + "="*60)
            print("🎉 TEST DATA INJECTION COMPLETE!")
            print("="*60)
            self.show_system_stats()
            
            print("\n📖 What you can test now:")
            print("   • API Docs: http://localhost:8000/docs")
            print("   • System Stats: http://localhost:8000/stats")
            print("   • Security Audits: http://localhost:8000/security-audits")
            print("   • Repository List: http://localhost:8000/repositories")
            
            print("\n🧪 Test commands:")
            print("   curl http://localhost:8000/stats")
            print("   curl -X POST http://localhost:8000/agent-query \\")
            print("     -H 'Content-Type: application/json' \\")
            print("     -d '{\"query\": \"What repositories are protected?\"}'")
            
            return True
            
        except Exception as e:
            print(f"❌ Test data injection failed: {e}")
            return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Inject test data into GitHub Protection Agent")
    parser.add_argument("--agent-url", default="http://localhost:8000", help="Agent URL")
    parser.add_argument("--quick", action="store_true", help="Quick injection (fewer repos)")
    
    args = parser.parse_args()
    
    injector = TestDataInjector(args.agent_url)
    
    if args.quick:
        print("🚀 Quick Test Data Injection")
        print("="*40)
        
        # Quick version - just register 2 repos and test basic functionality
        if not injector.check_agent_health():
            print("❌ Agent not running!")
            return False
        
        # Register just 2 of your repos for quick testing
        quick_repos = [
            {
                "github_url": "https://github.com/AMRITESH240304/AgentMint",
                "license_type": "MIT",
                "description": "AgentMint - AI agent minting platform"
            },
            {
                "github_url": "https://github.com/ETIM-PAUL/AirClaim",
                "license_type": "MIT",
                "description": "AirClaim - Airdrop claiming platform"
            }
        ]
        
        for repo in quick_repos:
            try:
                response = requests.post(f"{args.agent_url}/register-repository", json=repo)
                if response.status_code == 200 and response.json().get('success'):
                    print(f"✅ Registered {repo['github_url'].split('/')[-1]}")
                else:
                    print(f"❌ Failed to register {repo['github_url'].split('/')[-1]}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # Test one query
        try:
            response = requests.post(
                f"{args.agent_url}/agent-query",
                json={"query": "How many repositories are protected?"}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"🤖 Agent response: {result.get('response', '')[:100]}...")
        except:
            pass
        
        print("✅ Quick injection complete!")
        return True
    else:
        return injector.inject_all_test_data()

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)