# initialize_contract.py - Script to populate contract with initial data

import hashlib
import json
import time
from datetime import datetime
from typing import List, Dict
import requests
from web3 import Web3
from eth_account import Account
import os

class ContractInitializer:
    def __init__(self, contract_address: str, private_key: str = None):
        self.contract_address = contract_address
        
        # Flow Testnet configuration
        self.rpc_url = "https://testnet.evm.nodes.onflow.org"
        self.chain_id = 545
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        if private_key:
            self.account = Account.from_key(private_key)
        else:
            self.account = None
            
        print(f"🌊 Connected to Flow EVM Testnet")
        print(f"📡 Contract: {contract_address}")
        print(f"🔗 Connected: {self.w3.is_connected()}")

    def create_sample_repositories(self) -> List[Dict]:
        """Create sample repository data for testing"""
        
        sample_repos = [
            {
                "github_url": "https://github.com/onflow/flow-go",
                "name": "flow-go",
                "description": "Flow blockchain implementation in Go",
                "language": "Go",
                "license_type": "Apache-2.0",
                "owner": "onflow"
            },
            {
                "github_url": "https://github.com/onflow/cadence",
                "name": "cadence",
                "description": "Cadence smart contract language",
                "language": "Go", 
                "license_type": "Apache-2.0",
                "owner": "onflow"
            },
            {
                "github_url": "https://github.com/microsoft/vscode",
                "name": "vscode",
                "description": "Visual Studio Code editor",
                "language": "TypeScript",
                "license_type": "MIT",
                "owner": "microsoft"
            },
            {
                "github_url": "https://github.com/facebook/react",
                "name": "react",
                "description": "React JavaScript library",
                "language": "JavaScript",
                "license_type": "MIT", 
                "owner": "facebook"
            },
            {
                "github_url": "https://github.com/ethereum/solidity",
                "name": "solidity",
                "description": "Solidity smart contract language",
                "language": "C++",
                "license_type": "GPL-3.0",
                "owner": "ethereum"
            }
        ]
        
        # Process each repository
        processed_repos = []
        for repo in sample_repos:
            # Generate fingerprint data
            fingerprint_data = {
                'name': repo['name'],
                'description': repo['description'],
                'language': repo['language'],
                'github_url': repo['github_url'],
                'created_at': datetime.now().isoformat(),
            }
            
            # Generate hashes
            repo_hash = hashlib.sha256(
                json.dumps(fingerprint_data, sort_keys=True).encode()
            ).hexdigest()
            
            fingerprint = hashlib.sha256(
                f"{repo['owner']}/{repo['name']}{repo['github_url']}".encode()
            ).hexdigest()
            
            # Generate key features
            key_features = [
                f"{repo['language']} implementation",
                f"{repo['name']} core functionality",
                f"Open source {repo['license_type']} licensed",
                f"Maintained by {repo['owner']}"
            ]
            
            processed_repo = {
                **repo,
                'repo_hash': repo_hash,
                'fingerprint': fingerprint,
                'key_features': key_features,
                'processed_at': datetime.now().isoformat()
            }
            
            processed_repos.append(processed_repo)
            
        return processed_repos

    def simulate_contract_registration(self, repo_data: Dict) -> Dict:
        """Simulate registering repository on blockchain"""
        print(f"📝 Simulating contract registration for: {repo_data['name']}")
        
        # Simulate transaction
        tx_hash = f"0x{hashlib.sha256(f'{repo_data["github_url"]}{time.time()}'.encode()).hexdigest()}"
        
        # Simulate gas usage
        gas_used = 150000 + len(repo_data['key_features']) * 5000
        
        result = {
            'success': True,
            'tx_hash': tx_hash,
            'contract_address': self.contract_address,
            'gas_used': gas_used,
            'network': 'Flow Testnet',
            'block_number': int(time.time()) % 1000000,  # Simulate block number
            'registered_at': datetime.now().isoformat()
        }
        
        print(f"   ✅ Transaction: {tx_hash[:16]}...")
        print(f"   ⛽ Gas Used: {gas_used:,}")
        
        return result

    def create_sample_violations(self, repositories: List[Dict]) -> List[Dict]:
        """Create sample violation data"""
        
        sample_violations = [
            {
                "original_repo": repositories[0],  # flow-go
                "violating_url": "https://github.com/fake-user/flow-copy",
                "similarity_score": 0.85,
                "reason": "Copied core Flow blockchain implementation"
            },
            {
                "original_repo": repositories[2],  # vscode
                "violating_url": "https://github.com/clone-user/code-editor",
                "similarity_score": 0.72,
                "reason": "Similar editor functionality and UI patterns"
            },
            {
                "original_repo": repositories[3],  # react
                "violating_url": "https://github.com/copy-cat/react-clone",
                "similarity_score": 0.91,
                "reason": "Direct copy of React component system"
            }
        ]
        
        processed_violations = []
        for i, violation in enumerate(sample_violations):
            # Generate evidence hash
            evidence = {
                'violating_url': violation['violating_url'],
                'similarity_score': violation['similarity_score'],
                'reason': violation['reason'],
                'detected_at': datetime.now().isoformat()
            }
            
            evidence_hash = hashlib.sha256(
                json.dumps(evidence, sort_keys=True).encode()
            ).hexdigest()
            
            # Simulate blockchain transaction
            tx_hash = f"0x{hashlib.sha256(f'{violation["violating_url"]}{time.time()}'.encode()).hexdigest()}"
            
            processed_violation = {
                'violation_id': i + 1,
                'original_repo_id': repositories.index(violation['original_repo']) + 1,
                'original_repo_name': violation['original_repo']['name'],
                'violating_url': violation['violating_url'],
                'similarity_score': violation['similarity_score'],
                'reason': violation['reason'],
                'evidence_hash': evidence_hash,
                'tx_hash': tx_hash,
                'status': 'pending',
                'reported_at': datetime.now().isoformat()
            }
            
            processed_violations.append(processed_violation)
            
        return processed_violations

    def initialize_contract_data(self) -> Dict:
        """Initialize contract with sample data"""
        print("🚀 Initializing contract with sample data...")
        print("="*60)
        
        # Step 1: Create sample repositories
        print("📁 Creating sample repositories...")
        repositories = self.create_sample_repositories()
        
        # Step 2: Register repositories
        print(f"\n📝 Registering {len(repositories)} repositories...")
        registered_repos = []
        
        for i, repo in enumerate(repositories):
            repo_id = i + 1
            registration_result = self.simulate_contract_registration(repo)
            
            # Combine repo data with registration result
            full_repo_data = {
                'repo_id': repo_id,
                **repo,
                **registration_result
            }
            
            registered_repos.append(full_repo_data)
            time.sleep(1)  # Simulate transaction delay
        
        # Step 3: Create sample violations
        print(f"\n⚠️ Creating sample violations...")
        violations = self.create_sample_violations(repositories)
        
        for violation in violations:
            print(f"   📋 Violation: {violation['violating_url']}")
            print(f"      Similarity: {violation['similarity_score']:.1%}")
            print(f"      Reason: {violation['reason']}")
            
        # Step 4: Generate summary
        summary = {
            'initialization_completed_at': datetime.now().isoformat(),
            'contract_address': self.contract_address,
            'network': 'Flow Testnet',
            'repositories_registered': len(registered_repos),
            'violations_created': len(violations),
            'total_gas_used': sum(repo.get('gas_used', 0) for repo in registered_repos),
            'repositories': registered_repos,
            'violations': violations
        }
        
        return summary

    def save_initialization_data(self, data: Dict, filename: str = "contract_initialization.json"):
        """Save initialization data to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"💾 Initialization data saved to: {filename}")
            return True
        except Exception as e:
            print(f"❌ Failed to save data: {e}")
            return False

class AgentDataSeeder:
    """Seeds the agent's in-memory storage with initial data"""
    
    def __init__(self, agent_url: str = "http://localhost:8000"):
        self.agent_url = agent_url
        
    def check_agent_health(self) -> bool:
        """Check if agent is running and healthy"""
        try:
            response = requests.get(f"{self.agent_url}/")
            if response.status_code == 200:
                data = response.json()
                return data.get('agent_ready', False)
            return False
        except Exception as e:
            print(f"❌ Agent health check failed: {e}")
            return False
    
    def seed_repositories(self, repositories: List[Dict]) -> List[Dict]:
        """Seed agent with repository data"""
        print(f"🌱 Seeding agent with {len(repositories)} repositories...")
        
        seeded_repos = []
        for repo in repositories:
            try:
                # Register repository with agent
                response = requests.post(
                    f"{self.agent_url}/register-repository",
                    json={
                        "github_url": repo['github_url'],
                        "license_type": repo['license_type'],
                        "description": repo['description']
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print(f"   ✅ {repo['name']}: Registered with ID {result.get('repo_id')}")
                        seeded_repos.append({**repo, 'agent_repo_id': result.get('repo_id')})
                    else:
                        print(f"   ❌ {repo['name']}: Registration failed")
                else:
                    print(f"   ❌ {repo['name']}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ {repo['name']}: Error - {e}")
                
            time.sleep(2)  # Avoid overwhelming the agent
            
        return seeded_repos
    
    def trigger_security_audits(self, repositories: List[Dict]) -> List[Dict]:
        """Trigger security audits for repositories"""
        print(f"🔒 Triggering security audits...")
        
        audit_results = []
        for repo in repositories[:3]:  # Limit to first 3 to avoid long wait
            try:
                print(f"   🔍 Auditing {repo['name']}...")
                
                response = requests.post(
                    f"{self.agent_url}/security-audit",
                    json={
                        "github_url": repo['github_url'],
                        "audit_type": "comprehensive"
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print(f"      ✅ Audit completed - ID: {result.get('audit_id')}")
                        audit_results.append(result)
                    else:
                        print(f"      ❌ Audit failed")
                else:
                    print(f"      ❌ HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ Error: {e}")
                
            time.sleep(3)  # Security audits take time
            
        return audit_results

def main():
    """Main initialization function"""
    
    # Configuration
    contract_address = os.getenv('CONTRACT_ADDRESS', '0x5fa19b4a48C20202055c8a6fdf16688633617D50')
    private_key = os.getenv('PRIVATE_KEY')
    agent_url = os.getenv('AGENT_URL', 'http://localhost:8000')
    
    print("🚀 GitHub Protection Agent Initialization Script")
    print("="*60)
    print(f"📡 Contract: {contract_address}")
    print(f"🤖 Agent URL: {agent_url}")
    print(f"🔑 Private Key: {'Set' if private_key else 'Not Set'}")
    print()
    
    # Step 1: Initialize contract data
    print("Step 1: Initializing contract data...")
    initializer = ContractInitializer(contract_address, private_key)
    
    try:
        init_data = initializer.initialize_contract_data()
        print(f"✅ Contract initialization completed!")
        print(f"   Repositories: {init_data['repositories_registered']}")
        print(f"   Violations: {init_data['violations_created']}")
        print(f"   Gas Used: {init_data['total_gas_used']:,}")
        
        # Save initialization data
        initializer.save_initialization_data(init_data)
        
    except Exception as e:
        print(f"❌ Contract initialization failed: {e}")
        return False
    
    # Step 2: Check if agent is running
    print(f"\nStep 2: Checking agent status...")
    seeder = AgentDataSeeder(agent_url)
    
    if not seeder.check_agent_health():
        print("❌ Agent is not running or not ready!")
        print("   Please start the agent first:")
        print("   python enhanced_fastapi_server.py")
        
        # Ask user if they want to continue with just contract init
        user_input = input("\nContinue with contract initialization only? (y/n): ")
        if user_input.lower() != 'y':
            return False
        print("✅ Contract initialization completed. Start agent and run seeding later.")
        return True
    
    print("✅ Agent is healthy and ready!")
    
    # Step 3: Seed agent with repository data
    print(f"\nStep 3: Seeding agent with data...")
    try:
        seeded_repos = seeder.seed_repositories(init_data['repositories'])
        print(f"✅ Seeded {len(seeded_repos)} repositories into agent")
        
        # Step 4: Trigger some security audits
        print(f"\nStep 4: Triggering security audits...")
        audit_results = seeder.trigger_security_audits(seeded_repos)
        print(f"✅ Completed {len(audit_results)} security audits")
        
    except Exception as e:
        print(f"❌ Agent seeding failed: {e}")
        return False
    
    # Final summary
    print("\n" + "="*60)
    print("🎉 INITIALIZATION COMPLETE!")
    print("="*60)
    print(f"✅ Contract initialized with sample data")
    print(f"✅ Agent seeded with {len(seeded_repos)} repositories")
    print(f"✅ {len(audit_results)} security audits completed")
    print(f"✅ Ready for testing!")
    print()
    print("Next steps:")
    print("1. Test the agent: python test_agent.py quick")
    print("2. View API docs: http://localhost:8000/docs")
    print("3. Check system stats: http://localhost:8000/stats")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)