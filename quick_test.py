# quick_test.py - Quick verification of your agent

import requests
import json
import time

def test_agent():
    """Quick test of agent functionality"""
    agent_url = "http://localhost:8000"
    
    print("🧪 Quick Agent Test")
    print("="*30)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{agent_url}/")
        if response.status_code == 200:
            print("✅ Agent is running")
            data = response.json()
            print(f"   Version: {data.get('version')}")
            print(f"   AI Backend: {data.get('ai_backend', {}).get('current')}")
        else:
            print("❌ Agent health check failed")
            return False
    except Exception as e:
        print(f"❌ Can't connect to agent: {e}")
        print("   Start agent with: python bootstrap_agent.py")
        return False
    
    # Test 2: Stats
    try:
        response = requests.get(f"{agent_url}/stats")
        if response.status_code == 200:
            stats = response.json()
            repos = stats.get('statistics', {}).get('repositories', {}).get('total_tracked', 0)
            audits = stats.get('statistics', {}).get('security_audits', {}).get('total_completed', 0)
            print(f"✅ Stats: {repos} repos, {audits} audits")
        else:
            print("⚠️ Stats unavailable")
    except:
        print("⚠️ Stats error")
    
    # Test 3: Quick repository registration
    try:
        test_repo = {
            "github_url": "https://github.com/AMRITESH240304/AgentMint",
            "license_type": "MIT",
            "description": "AgentMint - AI agent minting platform for testing"
        }
        
        response = requests.post(f"{agent_url}/register-repository", json=test_repo, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Repository registration works (ID: {result.get('repo_id')})")
            else:
                print(f"⚠️ Registration failed: {result.get('error')}")
        else:
            print(f"❌ Registration HTTP {response.status_code}")
    except Exception as e:
        print(f"⚠️ Registration error: {e}")
    
    # Test 4: Agent query
    try:
        response = requests.post(
            f"{agent_url}/agent-query",
            json={"query": "What can you help me with?"},
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Natural language queries work")
                print(f"   Response: {result.get('response', '')[:80]}...")
            else:
                print("⚠️ Query failed")
        else:
            print(f"❌ Query HTTP {response.status_code}")
    except Exception as e:
        print(f"⚠️ Query error: {e}")
    
    print("\n🎉 Quick test complete!")
    print("📚 Full docs: http://localhost:8000/docs")
    return True

if __name__ == "__main__":
    test_agent()