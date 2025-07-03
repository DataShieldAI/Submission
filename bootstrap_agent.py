# bootstrap_agent.py - Complete agent bootstrap script

import os
import sys
import time
import json
import subprocess
import signal
import threading
from pathlib import Path
import requests

class AgentBootstrap:
    def __init__(self):
        self.agent_process = None
        self.agent_url = "http://localhost:8000"
        self.contract_address = os.getenv('CONTRACT_ADDRESS', '0x5fa19b4a48C20202055c8a6fdf16688633617D50')
        
    def check_environment(self) -> bool:
        """Check required environment variables"""
        print("🔍 Checking environment...")
        
        required_vars = {
            'CONTRACT_ADDRESS': self.contract_address,
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN', 'Not set (optional)')
        }
        
        missing_required = []
        
        for var, value in required_vars.items():
            if var == 'OPENAI_API_KEY' and not value and os.getenv('USE_LOCAL_MODEL') != 'true':
                missing_required.append(var)
            elif var == 'CONTRACT_ADDRESS' and not value:
                missing_required.append(var)
            
            status = "✅" if value and value != 'Not set (optional)' else "❌" if var in ['OPENAI_API_KEY', 'CONTRACT_ADDRESS'] else "⚠️"
            print(f"   {status} {var}: {value[:20] + '...' if value and len(str(value)) > 20 else value}")
        
        if missing_required:
            print(f"\n❌ Missing required environment variables: {missing_required}")
            print("Please set them and try again:")
            for var in missing_required:
                print(f"   export {var}='your_value_here'")
            return False
        
        print("✅ Environment check passed!")
        return True
    
    def check_dependencies(self) -> bool:
        """Check if required Python packages are installed"""
        print("📦 Checking dependencies...")
        
        required_packages = [
            'fastapi', 'uvicorn', 'langchain', 'langchain_openai', 
            'requests', 'GitPython', 'web3', 'eth_account'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"   ✅ {package}")
            except ImportError:
                print(f"   ❌ {package}")
                missing_packages.append(package)
        
        if missing_packages:
            print(f"\n❌ Missing packages: {missing_packages}")
            print("Install them with:")
            print(f"   pip install {' '.join(missing_packages)}")
            return False
        
        print("✅ All dependencies available!")
        return True
    
    def check_agent_files(self) -> bool:
        """Check if agent files exist"""
        print("📁 Checking agent files...")
        
        required_files = [
            'enhanced_fastapi_server.py',
            'enhanced_agent_with_security.py'
        ]
        
        missing_files = []
        
        for file in required_files:
            if os.path.exists(file):
                print(f"   ✅ {file}")
            else:
                print(f"   ❌ {file}")
                missing_files.append(file)
        
        if missing_files:
            print(f"\n❌ Missing agent files: {missing_files}")
            return False
        
        print("✅ All agent files present!")
        return True
    
    def start_agent_server(self) -> bool:
        """Start the agent server"""
        print("🚀 Starting agent server...")
        
        try:
            # Start the agent server
            self.agent_process = subprocess.Popen(
                [sys.executable, 'enhanced_fastapi_server.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            print(f"   Started with PID: {self.agent_process.pid}")
            
            # Wait for server to be ready
            print("   Waiting for server to be ready...")
            
            for attempt in range(30):  # 30 second timeout
                try:
                    response = requests.get(f"{self.agent_url}/", timeout=2)
                    if response.status_code == 200:
                        print("   ✅ Server is ready!")
                        return True
                except requests.exceptions.RequestException:
                    pass
                
                time.sleep(1)
                print(".", end="", flush=True)
            
            print("\n   ❌ Server failed to start within 30 seconds")
            return False
            
        except Exception as e:
            print(f"   ❌ Failed to start server: {e}")
            return False
    
    def verify_agent_health(self) -> bool:
        """Verify agent is healthy and ready"""
        print("🏥 Verifying agent health...")
        
        try:
            response = requests.get(f"{self.agent_url}/")
            if response.status_code == 200:
                data = response.json()
                
                print(f"   ✅ Service: {data.get('service', 'Unknown')}")
                print(f"   ✅ Version: {data.get('version', 'Unknown')}")
                print(f"   ✅ Agent Ready: {data.get('agent_ready', False)}")
                print(f"   ✅ AI Backend: {data.get('ai_backend', {}).get('current', 'Unknown')}")
                
                return data.get('agent_ready', False)
            else:
                print(f"   ❌ HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Health check failed: {e}")
            return False
    
    def initialize_contract_data(self) -> bool:
        """Initialize contract with sample data"""
        print("📝 Initializing contract data...")
        
        try:
            # Import and run the contract initializer
            from initialize_contract import ContractInitializer
            
            initializer = ContractInitializer(
                contract_address=self.contract_address,
                private_key=os.getenv('PRIVATE_KEY')
            )
            
            init_data = initializer.initialize_contract_data()
            
            # Save the data
            initializer.save_initialization_data(init_data, 'bootstrap_contract_data.json')
            
            print(f"   ✅ Repositories: {init_data['repositories_registered']}")
            print(f"   ✅ Violations: {init_data['violations_created']}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Contract initialization failed: {e}")
            return False
    
    def seed_agent_data(self) -> bool:
        """Seed agent with initial data"""
        print("🌱 Seeding agent with data...")
        
        try:
            # Load contract data if available
            contract_data_file = 'bootstrap_contract_data.json'
            if os.path.exists(contract_data_file):
                with open(contract_data_file, 'r') as f:
                    contract_data = json.load(f)
                repositories = contract_data.get('repositories', [])
            else:
                # Create minimal sample data
                repositories = [
                    {
                        "github_url": "https://github.com/onflow/flow-go",
                        "name": "flow-go",
                        "license_type": "Apache-2.0",
                        "description": "Flow blockchain implementation"
                    },
                    {
                        "github_url": "https://github.com/facebook/react", 
                        "name": "react",
                        "license_type": "MIT",
                        "description": "React JavaScript library"
                    }
                ]
            
            # Seed repositories
            seeded_count = 0
            for repo in repositories[:3]:  # Limit to first 3
                try:
                    response = requests.post(
                        f"{self.agent_url}/register-repository",
                        json={
                            "github_url": repo['github_url'],
                            "license_type": repo.get('license_type', 'MIT'),
                            "description": repo.get('description', '')
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success'):
                            print(f"   ✅ {repo['name']}: ID {result.get('repo_id')}")
                            seeded_count += 1
                        else:
                            print(f"   ❌ {repo['name']}: {result.get('error', 'Unknown error')}")
                    else:
                        print(f"   ❌ {repo['name']}: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ {repo['name']}: {e}")
                
                time.sleep(2)  # Avoid overwhelming the agent
            
            print(f"   ✅ Seeded {seeded_count} repositories")
            return seeded_count > 0
            
        except Exception as e:
            print(f"   ❌ Agent seeding failed: {e}")
            return False
    
    def run_quick_test(self) -> bool:
        """Run a quick test to verify everything works"""
        print("🧪 Running quick verification test...")
        
        tests = [
            ("Health Check", f"{self.agent_url}/"),
            ("Agent Status", f"{self.agent_url}/agent-status"),
            ("System Stats", f"{self.agent_url}/stats")
        ]
        
        passed = 0
        
        for test_name, url in tests:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"   ✅ {test_name}")
                    passed += 1
                else:
                    print(f"   ❌ {test_name}: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ {test_name}: {e}")
        
        # Test a simple analysis
        try:
            response = requests.post(
                f"{self.agent_url}/analyze-repository",
                json={"github_url": "https://github.com/facebook/react"},
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✅ Repository Analysis")
                    passed += 1
                else:
                    print(f"   ❌ Repository Analysis: {result.get('error')}")
            else:
                print(f"   ❌ Repository Analysis: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Repository Analysis: {e}")
        
        print(f"   📊 Tests passed: {passed}/{len(tests) + 1}")
        return passed >= len(tests)  # Allow analysis to fail
    
    def run_comprehensive_tests(self) -> bool:
        """Run comprehensive tests of all agent features"""
        print("🔬 Running comprehensive feature tests...")
        
        test_repo = "https://github.com/microsoft/vscode"
        
        tests = [
            ("URL Cleaning", "clean-urls", {"url_text": "Check out github.com/microsoft/vscode and https://github.com/facebook/react"}),
            ("Repository Analysis", "analyze-repository", {"github_url": test_repo}),
            ("Security Audit", "security-audit", {"github_url": test_repo, "audit_type": "comprehensive"}),
            ("Full Workflow", "full-protection-workflow", {"github_url": test_repo, "license_type": "MIT"})
        ]
        
        passed = 0
        
        for test_name, endpoint, data in tests:
            try:
                print(f"   🧪 Testing {test_name}...")
                response = requests.post(
                    f"{self.agent_url}/{endpoint}",
                    json=data,
                    timeout=60  # Longer timeout for comprehensive tests
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success', True):  # Some endpoints don't have 'success' field
                        print(f"      ✅ {test_name}")
                        passed += 1
                    else:
                        print(f"      ❌ {test_name}: {result.get('error', 'Unknown error')}")
                else:
                    print(f"      ❌ {test_name}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ {test_name}: {e}")
            
            time.sleep(2)  # Rate limiting
        
        # Test agent query
        try:
            print("   🧪 Testing Natural Language Query...")
            response = requests.post(
                f"{self.agent_url}/agent-query",
                json={"query": "How many repositories are currently protected?"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"      ✅ Natural Language Query")
                    print(f"         Response: {result.get('response', '')[:100]}...")
                    passed += 1
                else:
                    print(f"      ❌ Natural Language Query: {result.get('error')}")
            else:
                print(f"      ❌ Natural Language Query: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Natural Language Query: {e}")
        
        print(f"   📊 Comprehensive tests passed: {passed}/{len(tests) + 1}")
        return passed >= (len(tests) // 2)  # Pass if at least half work
    
    def show_usage_examples(self):
        """Show usage examples"""
        print("\n📖 USAGE EXAMPLES:")
        print("="*50)
        
        examples = [
            ("Health Check", "GET", "/", None),
            ("System Stats", "GET", "/stats", None),
            ("Clean URLs", "POST", "/clean-urls", {"url_text": "Check out github.com/user/repo"}),
            ("Analyze Repo", "POST", "/analyze-repository", {"github_url": "https://github.com/facebook/react"}),
            ("Security Audit", "POST", "/security-audit", {"github_url": "https://github.com/user/repo"}),
            ("Register Repo", "POST", "/register-repository", {"github_url": "https://github.com/user/repo", "license_type": "MIT"}),
            ("Ask Agent", "POST", "/agent-query", {"query": "How does repository protection work?"})
        ]
        
        for name, method, endpoint, body in examples:
            print(f"\n{name}:")
            if method == "GET":
                print(f"  curl {self.agent_url}{endpoint}")
            else:
                if body:
                    body_str = json.dumps(body, indent=2)
                    print(f"  curl -X {method} {self.agent_url}{endpoint} \\")
                    print(f"    -H 'Content-Type: application/json' \\")
                    print(f"    -d '{json.dumps(body)}'")
                else:
                    print(f"  curl -X {method} {self.agent_url}{endpoint}")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.agent_process:
            print("🧹 Stopping agent server...")
            try:
                self.agent_process.terminate()
                self.agent_process.wait(timeout=5)
                print("   ✅ Server stopped")
            except subprocess.TimeoutExpired:
                print("   ⚠️ Force killing server...")
                self.agent_process.kill()
            except Exception as e:
                print(f"   ❌ Error stopping server: {e}")
    
    def bootstrap(self, keep_running: bool = True, run_comprehensive: bool = False) -> bool:
        """Complete bootstrap process"""
        print("🚀 GitHub Protection Agent Bootstrap")
        print("="*50)
        
        try:
            # Step 1: Environment check
            if not self.check_environment():
                return False
            
            # Step 2: Dependencies check  
            if not self.check_dependencies():
                return False
            
            # Step 3: Files check
            if not self.check_agent_files():
                return False
            
            # Step 4: Initialize contract data
            if not self.initialize_contract_data():
                print("⚠️ Contract initialization failed, continuing with minimal data...")
            
            # Step 5: Start agent server
            if not self.start_agent_server():
                return False
            
            # Step 6: Verify health
            if not self.verify_agent_health():
                return False
            
            # Step 7: Seed agent data
            if not self.seed_agent_data():
                print("⚠️ Agent seeding failed, but agent is running...")
            
            # Step 8: Quick test
            if not self.run_quick_test():
                print("⚠️ Some tests failed, but agent is functional...")
            
            # Step 9: Comprehensive tests (optional)
            if run_comprehensive:
                if not self.run_comprehensive_tests():
                    print("⚠️ Some comprehensive tests failed...")
            
            # Success!
            print("\n🎉 BOOTSTRAP COMPLETE!")
            print("="*50)
            print("✅ Agent is running and ready!")
            print(f"🌐 API: {self.agent_url}")
            print(f"📚 Docs: {self.agent_url}/docs")
            print(f"📊 Stats: {self.agent_url}/stats")
            
            self.show_usage_examples()
            
            if keep_running:
                print("\n⌨️ Press Ctrl+C to stop the agent")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n👋 Shutting down...")
                    self.cleanup()
            
            return True
            
        except Exception as e:
            print(f"❌ Bootstrap failed: {e}")
            return False
        finally:
            if not keep_running:
                self.cleanup()

def main():
    """Main function with command line arguments"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Bootstrap GitHub Protection Agent")
    parser.add_argument("--no-keep-running", action="store_true", help="Don't keep the server running")
    parser.add_argument("--comprehensive", action="store_true", help="Run comprehensive tests")
    parser.add_argument("--quick", action="store_true", help="Quick start without comprehensive tests")
    
    args = parser.parse_args()
    
    bootstrap = AgentBootstrap()
    
    # Set up signal handler for graceful shutdown
    def signal_handler(sig, frame):
        print("\n🛑 Received interrupt signal...")
        bootstrap.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        success = bootstrap.bootstrap(
            keep_running=not args.no_keep_running,
            run_comprehensive=args.comprehensive
        )
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        bootstrap.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()