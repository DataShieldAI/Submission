# test_agent.py - Comprehensive test script for GitHub Protection Agent

import requests
import json
import time
from typing import Dict, List
import os

class GitHubProtectionTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_health_check(self) -> Dict:
        """Test basic health check"""
        print("🏥 Testing health check...")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed")
                print(f"   Service: {data.get('service')}")
                print(f"   Version: {data.get('version')}")
                print(f"   Agent Ready: {data.get('agent_ready')}")
                print(f"   AI Backend: {data.get('ai_backend', {}).get('current')}")
                return {"success": True, "data": data}
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return {"success": False, "error": str(e)}

    def test_analyze_repository(self, github_url: str) -> Dict:
        """Test repository analysis"""
        print(f"🔍 Testing repository analysis: {github_url}")
        try:
            payload = {
                "github_url": github_url,
                "license_type": "MIT"
            }
            
            response = self.session.post(
                f"{self.base_url}/analyze-repository",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Analysis completed")
                print(f"   Success: {data.get('success')}")
                if data.get('success'):
                    print(f"   Repository Hash: {data.get('repo_hash', 'N/A')[:16]}...")
                    print(f"   Total Files: {data.get('total_files', 'N/A')}")
                    print(f"   Key Features: {data.get('key_features', 'N/A')[:100]}...")
                return {"success": True, "data": data}
            else:
                print(f"❌ Analysis failed: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return {"success": False, "error": str(e)}

    def test_security_audit(self, github_url: str) -> Dict:
        """Test security audit"""
        print(f"🔒 Testing security audit: {github_url}")
        try:
            payload = {
                "github_url": github_url,
                "audit_type": "comprehensive",
                "include_private_keys": True,
                "include_vulnerabilities": True
            }
            
            response = self.session.post(
                f"{self.base_url}/security-audit",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Security audit completed")
                print(f"   Success: {data.get('success')}")
                if data.get('success'):
                    print(f"   Files Scanned: {data.get('files_scanned', 'N/A')}")
                    print(f"   Total Findings: {data.get('total_findings', 'N/A')}")
                    print(f"   Critical: {data.get('critical_findings', 'N/A')}")
                    print(f"   High: {data.get('high_findings', 'N/A')}")
                return {"success": True, "data": data}
            else:
                print(f"❌ Security audit failed: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Security audit failed: {e}")
            return {"success": False, "error": str(e)}

    def test_register_repository(self, github_url: str) -> Dict:
        """Test repository registration"""
        print(f"📝 Testing repository registration: {github_url}")
        try:
            payload = {
                "github_url": github_url,
                "license_type": "MIT",
                "description": "Test repository for GitHub Protection Agent"
            }
            
            response = self.session.post(
                f"{self.base_url}/register-repository",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Registration completed")
                print(f"   Success: {data.get('success')}")
                if data.get('success'):
                    print(f"   Repository ID: {data.get('repo_id', 'N/A')}")
                    print(f"   Transaction Hash: {data.get('tx_hash', 'N/A')[:16]}...")
                return {"success": True, "data": data}
            else:
                print(f"❌ Registration failed: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Registration failed: {e}")
            return {"success": False, "error": str(e)}

    def test_search_violations(self, repo_id: int) -> Dict:
        """Test violation search"""
        print(f"🔎 Testing violation search for repo ID: {repo_id}")
        try:
            response = self.session.post(f"{self.base_url}/search-violations/{repo_id}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Violation search completed")
                print(f"   Success: {data.get('success')}")
                print(f"   Violations Found: {data.get('violations_found', 'N/A')}")
                return {"success": True, "data": data}
            else:
                print(f"❌ Violation search failed: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Violation search failed: {e}")
            return {"success": False, "error": str(e)}

    def test_agent_query(self, query: str) -> Dict:
        """Test natural language agent query"""
        print(f"🤖 Testing agent query: {query}")
        try:
            payload = {
                "query": query,
                "context": {"test": True}
            }
            
            response = self.session.post(
                f"{self.base_url}/agent-query",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Agent query completed")
                print(f"   Success: {data.get('success')}")
                if data.get('success'):
                    print(f"   Response: {data.get('response', 'N/A')[:200]}...")
                return {"success": True, "data": data}
            else:
                print(f"❌ Agent query failed: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Agent query failed: {e}")
            return {"success": False, "error": str(e)}

    def test_full_workflow(self, github_url: str) -> Dict:
        """Test complete protection workflow"""
        print(f"🚀 Testing full protection workflow: {github_url}")
        try:
            payload = {
                "github_url": github_url,
                "license_type": "MIT"
            }
            
            response = self.session.post(
                f"{self.base_url}/full-protection-workflow",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Full workflow completed")
                print(f"   Success: {data.get('success')}")
                if data.get('success'):
                    workflow_result = data.get('workflow_result', {})
                    print(f"   Analysis: {'✅' if workflow_result.get('analysis', {}).get('success') else '❌'}")
                    print(f"   Audit: {'✅' if workflow_result.get('audit', {}).get('success') else '❌'}")
                    print(f"   Registration: {'✅' if workflow_result.get('registration', {}).get('success') else '❌'}")
                return {"success": True, "data": data}
            else:
                print(f"❌ Full workflow failed: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Full workflow failed: {e}")
            return {"success": False, "error": str(e)}

    def test_get_stats(self) -> Dict:
        """Test getting system statistics"""
        print("📊 Testing system statistics...")
        try:
            response = self.session.get(f"{self.base_url}/stats")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Stats retrieved")
                print(f"   Success: {data.get('success')}")
                if data.get('success'):
                    stats = data.get('statistics', {})
                    repos = stats.get('repositories', {})
                    audits = stats.get('security_audits', {})
                    print(f"   Repositories Tracked: {repos.get('total_tracked', 'N/A')}")
                    print(f"   Security Audits: {audits.get('total_completed', 'N/A')}")
                return {"success": True, "data": data}
            else:
                print(f"❌ Stats failed: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Stats failed: {e}")
            return {"success": False, "error": str(e)}

    def run_comprehensive_test(self, test_repo_url: str = "https://github.com/facebook/react") -> Dict:
        """Run comprehensive test suite"""
        print("\n" + "="*70)
        print("🧪 COMPREHENSIVE GITHUB PROTECTION AGENT TEST SUITE")
        print("="*70)
        
        results = {}
        
        # Test 1: Health Check
        results['health_check'] = self.test_health_check()
        
        # Test 2: Repository Analysis
        results['analyze_repository'] = self.test_analyze_repository(test_repo_url)
        
        # Test 3: Security Audit
        results['security_audit'] = self.test_security_audit(test_repo_url)
        
        # Test 4: Repository Registration
        results['register_repository'] = self.test_register_repository(test_repo_url)
        
        # Test 5: Search Violations (if registration succeeded)
        if results['register_repository'].get('success'):
            repo_id = results['register_repository']['data'].get('repo_id', 1)
            results['search_violations'] = self.test_search_violations(repo_id)
        
        # Test 6: Agent Query
        results['agent_query'] = self.test_agent_query(
            "Analyze this repository for security vulnerabilities and explain the protection features available."
        )
        
        # Test 7: Full Workflow
        results['full_workflow'] = self.test_full_workflow(test_repo_url)
        
        # Test 8: System Stats
        results['stats'] = self.test_get_stats()
        
        # Summary
        print("\n" + "="*70)
        print("📋 TEST SUMMARY")
        print("="*70)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result.get('success'))
        
        for test_name, result in results.items():
            status = "✅ PASS" if result.get('success') else "❌ FAIL"
            print(f"   {test_name}: {status}")
            if not result.get('success'):
                print(f"      Error: {result.get('error', 'Unknown error')}")
        
        print(f"\nResults: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Your GitHub Protection Agent is working perfectly!")
        else:
            print("⚠️ Some tests failed. Check the errors above.")
        
        return results

# Quick test script
def quick_test():
    """Quick test function"""
    tester = GitHubProtectionTester()
    
    print("🚀 Quick GitHub Protection Agent Test")
    print("="*50)
    
    # Test health first
    health = tester.test_health_check()
    if not health.get('success'):
        print("❌ Server not running or not ready. Please start the server first:")
        print("   python enhanced_fastapi_server.py")
        return
    
    # Test with a simple repository
    test_repo = "https://github.com/microsoft/vscode"
    
    print(f"\n🔍 Testing with repository: {test_repo}")
    
    # Quick analysis
    analysis = tester.test_analyze_repository(test_repo)
    
    # Quick agent query
    query = tester.test_agent_query("What can you tell me about repository protection?")
    
    if analysis.get('success') and query.get('success'):
        print("\n🎉 Quick test passed! Your agent is working!")
    else:
        print("\n⚠️ Quick test had issues. Run full test for details.")

# Interactive test runner
def interactive_test():
    """Interactive test runner"""
    tester = GitHubProtectionTester()
    
    print("🤖 Interactive GitHub Protection Agent Tester")
    print("="*60)
    
    while True:
        print("\n📋 Available Tests:")
        print("1. Health Check")
        print("2. Analyze Repository")
        print("3. Security Audit")
        print("4. Register Repository")
        print("5. Agent Query")
        print("6. Full Workflow")
        print("7. System Stats")
        print("8. Comprehensive Test Suite")
        print("9. Quick Test")
        print("0. Exit")
        
        choice = input("\n🎯 Enter choice (0-9): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            tester.test_health_check()
        elif choice == "2":
            url = input("Enter GitHub URL: ").strip() or "https://github.com/facebook/react"
            tester.test_analyze_repository(url)
        elif choice == "3":
            url = input("Enter GitHub URL: ").strip() or "https://github.com/facebook/react"
            tester.test_security_audit(url)
        elif choice == "4":
            url = input("Enter GitHub URL: ").strip() or "https://github.com/facebook/react"
            tester.test_register_repository(url)
        elif choice == "5":
            query = input("Enter query: ").strip() or "What can you do?"
            tester.test_agent_query(query)
        elif choice == "6":
            url = input("Enter GitHub URL: ").strip() or "https://github.com/facebook/react"
            tester.test_full_workflow(url)
        elif choice == "7":
            tester.test_get_stats()
        elif choice == "8":
            url = input("Enter GitHub URL (or press Enter for default): ").strip()
            test_url = url if url else "https://github.com/facebook/react"
            tester.run_comprehensive_test(test_url)
        elif choice == "9":
            quick_test()
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            quick_test()
        elif sys.argv[1] == "comprehensive":
            tester = GitHubProtectionTester()
            repo_url = sys.argv[2] if len(sys.argv) > 2 else "https://github.com/facebook/react"
            tester.run_comprehensive_test(repo_url)
        elif sys.argv[1] == "interactive":
            interactive_test()
        else:
            print("Usage:")
            print("  python test_agent.py quick")
            print("  python test_agent.py comprehensive [repo_url]")
            print("  python test_agent.py interactive")
    else:
        interactive_test()