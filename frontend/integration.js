

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AGENT_API_BASE = process.env.REACT_APP_AGENT_API || 'http://localhost:8000';

// Main Dashboard Component
const GitHubProtectionDashboard = () => {
  const [repositories, setRepositories] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);

  // Register Repository Component
  const RepositoryRegistration = () => {
    const [githubUrl, setGithubUrl] = useState('');
    const [licenseType, setLicenseType] = useState('MIT');
    const [registering, setRegistering] = useState(false);

    const handleRegister = async () => {
      setRegistering(true);
      try {
        const response = await axios.post(`${AGENT_API_BASE}/register-repository`, {
          github_url: githubUrl,
          license_type: licenseType
        });
        
        console.log('Registration started:', response.data);
        // Poll for job completion
        pollJob(response.data.job_id);
      } catch (error) {
        console.error('Registration failed:', error);
      } finally {
        setRegistering(false);
      }
    };

    return (
      <div className="registration-form">
        <h3>Register Repository for Protection</h3>
        <input
          type="url"
          placeholder="https://github.com/username/repo"
          value={githubUrl}
          onChange={(e) => setGithubUrl(e.target.value)}
        />
        <select value={licenseType} onChange={(e) => setLicenseType(e.target.value)}>
          <option value="MIT">MIT</option>
          <option value="Apache-2.0">Apache 2.0</option>
          <option value="GPL-3.0">GPL 3.0</option>
          <option value="Custom">Custom</option>
        </select>
        <button onClick={handleRegister} disabled={registering}>
          {registering ? 'Registering...' : 'Register Repository'}
        </button>
      </div>
    );
  };

  // Security Audit Component
  const SecurityAudit = () => {
    const [auditUrl, setAuditUrl] = useState('');
    const [auditing, setAuditing] = useState(false);

    const handleAudit = async () => {
      setAuditing(true);
      try {
        const response = await axios.post(`${AGENT_API_BASE}/security-audit`, {
          github_url: auditUrl,
          audit_type: 'comprehensive'
        });
        
        console.log('Audit started:', response.data);
        pollJob(response.data.job_id);
      } catch (error) {
        console.error('Audit failed:', error);
      } finally {
        setAuditing(false);
      }
    };

    return (
      <div className="audit-form">
        <h3>Security Audit</h3>
        <input
          type="url"
          placeholder="https://github.com/username/repo"
          value={auditUrl}
          onChange={(e) => setAuditUrl(e.target.value)}
        />
        <button onClick={handleAudit} disabled={auditing}>
          {auditing ? 'Auditing...' : 'Start Security Audit'}
        </button>
      </div>
    );
  };

  // Natural Language Query Component
  const AgentQuery = () => {
    const [query, setQuery] = useState('');
    const [response, setResponse] = useState('');
    const [querying, setQuerying] = useState(false);

    const handleQuery = async () => {
      setQuerying(true);
      try {
        const response = await axios.post(`${AGENT_API_BASE}/agent-query`, {
          query: query
        });
        
        setResponse(response.data.response);
      } catch (error) {
        console.error('Query failed:', error);
        setResponse('Query failed: ' + error.message);
      } finally {
        setQuerying(false);
      }
    };

    return (
      <div className="agent-query">
        <h3>Ask the Agent</h3>
        <textarea
          placeholder="Ask me anything about your repositories, security, or code protection..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          rows={3}
        />
        <button onClick={handleQuery} disabled={querying}>
          {querying ? 'Asking...' : 'Ask Agent'}
        </button>
        {response && (
          <div className="response">
            <h4>Agent Response:</h4>
            <pre>{response}</pre>
          </div>
        )}
      </div>
    );
  };

  // Utility function to poll job status
  const pollJob = (jobId) => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`${AGENT_API_BASE}/job/${jobId}`);
        const job = response.data;
        
        if (job.status === 'completed' || job.status === 'failed') {
          clearInterval(interval);
          console.log('Job completed:', job);
          setJobs(prev => [...prev, job]);
        }
      } catch (error) {
        console.error('Error polling job:', error);
        clearInterval(interval);
      }
    }, 2000);

    // Clean up after 5 minutes
    setTimeout(() => clearInterval(interval), 300000);
  };

  return (
    <div className="dashboard">
      <h1>GitHub Repository Protection</h1>
      
      <div className="section">
        <RepositoryRegistration />
      </div>
      
      <div className="section">
        <SecurityAudit />
      </div>
      
      <div className="section">
        <AgentQuery />
      </div>
      
      <div className="section">
        <h3>Recent Jobs</h3>
        {jobs.map(job => (
          <div key={job.id} className={`job ${job.status}`}>
            <strong>{job.type}</strong> - {job.status}
            {job.result && <pre>{JSON.stringify(job.result, null, 2)}</pre>}
          </div>
        ))}
      </div>
    </div>
  );
};

// GitHub Actions Integration
// .github/workflows/protection.yml
const githubActionsWorkflow = `
name: Repository Protection
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  protect:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Register Repository
      run: |
        curl -X POST "${{ secrets.AGENT_API_URL }}/register-repository" \\
          -H "Content-Type: application/json" \\
          -d '{
            "github_url": "${{ github.server_url }}/${{ github.repository }}",
            "license_type": "MIT"
          }'
    
    - name: Security Audit
      run: |
        curl -X POST "${{ secrets.AGENT_API_URL }}/security-audit" \\
          -H "Content-Type: application/json" \\
          -d '{
            "github_url": "${{ github.server_url }}/${{ github.repository }}",
            "audit_type": "comprehensive"
          }'
    
    - name: Search for Violations
      run: |
        curl -X POST "${{ secrets.AGENT_API_URL }}/search-violations/1"
`;

// CLI Tool Integration
const cliExample = `
#!/usr/bin/env node
// github-protect-cli.js

const axios = require('axios');
const yargs = require('yargs');
const chalk = require('chalk');

const API_BASE = process.env.GITHUB_PROTECT_API || 'http://localhost:8000';

// Register command
yargs.command({
  command: 'register <url>',
  describe: 'Register a GitHub repository for protection',
  builder: {
    license: {
      type: 'string',
      default: 'MIT',
      describe: 'License type'
    }
  },
  handler: async (argv) => {
    console.log(chalk.blue('🔐 Registering repository...'));
    
    try {
      const response = await axios.post(\`\${API_BASE}/register-repository\`, {
        github_url: argv.url,
        license_type: argv.license
      });
      
      console.log(chalk.green('✅ Registration started!'));
      console.log('Job ID:', response.data.job_id);
      
      // Poll for completion
      await pollJob(response.data.job_id);
      
    } catch (error) {
      console.error(chalk.red('❌ Registration failed:'), error.message);
    }
  }
});

// Audit command
yargs.command({
  command: 'audit <url>',
  describe: 'Perform security audit on repository',
  handler: async (argv) => {
    console.log(chalk.blue('🔍 Starting security audit...'));
    
    try {
      const response = await axios.post(\`\${API_BASE}/security-audit\`, {
        github_url: argv.url,
        audit_type: 'comprehensive'
      });
      
      console.log(chalk.green('✅ Audit started!'));
      console.log('Job ID:', response.data.job_id);
      
      await pollJob(response.data.job_id);
      
    } catch (error) {
      console.error(chalk.red('❌ Audit failed:'), error.message);
    }
  }
});

// Ask command for natural language queries
yargs.command({
  command: 'ask <query>',
  describe: 'Ask the AI agent a question',
  handler: async (argv) => {
    console.log(chalk.blue('🤖 Asking agent...'));
    
    try {
      const response = await axios.post(\`\${API_BASE}/agent-query\`, {
        query: argv.query
      });
      
      console.log(chalk.green('🤖 Agent Response:'));
      console.log(response.data.response);
      
    } catch (error) {
      console.error(chalk.red('❌ Query failed:'), error.message);
    }
  }
});

// Monitor command
yargs.command({
  command: 'monitor <repo-id>',
  describe: 'Monitor repository for violations',
  handler: async (argv) => {
    console.log(chalk.blue('👀 Starting violation monitoring...'));
    
    try {
      const response = await axios.post(\`\${API_BASE}/search-violations/\${argv.repoId}\`);
      
      console.log(chalk.green('✅ Monitoring started!'));
      console.log('Job ID:', response.data.job_id);
      
      await pollJob(response.data.job_id);
      
    } catch (error) {
      console.error(chalk.red('❌ Monitoring failed:'), error.message);
    }
  }
});

async function pollJob(jobId) {
  console.log(chalk.yellow('⏳ Waiting for completion...'));
  
  while (true) {
    try {
      const response = await axios.get(\`\${API_BASE}/job/\${jobId}\`);
      const job = response.data;
      
      if (job.status === 'completed') {
        console.log(chalk.green('✅ Job completed successfully!'));
        if (job.result) {
          console.log('Result:', JSON.stringify(job.result, null, 2));
        }
        break;
      } else if (job.status === 'failed') {
        console.log(chalk.red('❌ Job failed:'), job.error);
        break;
      } else {
        process.stdout.write('.');
      }
      
      await new Promise(resolve => setTimeout(resolve, 2000));
      
    } catch (error) {
      console.error(chalk.red('❌ Error checking job status:'), error.message);
      break;
    }
  }
}

yargs.demandCommand(1, 'You need at least one command').help().argv;
`;

// Python SDK
const pythonSDK = \`
# github_protection_sdk.py

import requests
import time
from typing import Dict, List, Optional
import json

class GitHubProtectionClient:
    def __init__(self, api_base: str = "http://localhost:8000"):
        self.api_base = api_base.rstrip('/')
        self.session = requests.Session()
    
    def register_repository(self, github_url: str, license_type: str = "MIT") -> Dict:
        """Register a repository for protection"""
        response = self.session.post(
            f"{self.api_base}/register-repository",
            json={
                "github_url": github_url,
                "license_type": license_type
            }
        )
        response.raise_for_status()
        return response.json()
    
    def security_audit(self, github_url: str) -> Dict:
        """Perform security audit"""
        response = self.session.post(
            f"{self.api_base}/security-audit",
            json={
                "github_url": github_url,
                "audit_type": "comprehensive"
            }
        )
        response.raise_for_status()
        return response.json()
    
    def analyze_repository(self, github_url: str) -> Dict:
        """Analyze repository for key features"""
        response = self.session.post(
            f"{self.api_base}/analyze-repository",
            json={"github_url": github_url}
        )
        response.raise_for_status()
        return response.json()
    
    def search_violations(self, repo_id: int) -> Dict:
        """Search for code violations"""
        response = self.session.post(f"{self.api_base}/search-violations/{repo_id}")
        response.raise_for_status()
        return response.json()
    
    def report_violation(self, original_repo_id: int, violating_url: str, 
                        similarity_score: float) -> Dict:
        """Report a code violation"""
        response = self.session.post(
            f"{self.api_base}/report-violation",
            json={
                "original_repo_id": original_repo_id,
                "violating_url": violating_url,
                "similarity_score": similarity_score
            }
        )
        response.raise_for_status()
        return response.json()
    
    def ask_agent(self, query: str, context: Optional[Dict] = None) -> Dict:
        """Ask the AI agent a question"""
        payload = {"query": query}
        if context:
            payload["context"] = context
            
        response = self.session.post(
            f"{self.api_base}/agent-query",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def generate_license(self, repo_type: str, usage_requirements: str) -> Dict:
        """Generate appropriate license"""
        response = self.session.post(
            f"{self.api_base}/generate-license",
            json={
                "repo_type": repo_type,
                "usage_requirements": usage_requirements
            }
        )
        response.raise_for_status()
        return response.json()
    
    def full_protection_workflow(self, github_url: str, license_type: str = "MIT") -> Dict:
        """Run complete protection workflow"""
        response = self.session.post(
            f"{self.api_base}/full-protection-workflow",
            json={
                "github_url": github_url,
                "license_type": license_type
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_job_status(self, job_id: str) -> Dict:
        """Get job status"""
        response = self.session.get(f"{self.api_base}/job/{job_id}")
        response.raise_for_status()
        return response.json()
    
    def wait_for_job(self, job_id: str, timeout: int = 300) -> Dict:
        """Wait for job completion"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            job = self.get_job_status(job_id)
            
            if job['status'] in ['completed', 'failed']:
                return job
                
            time.sleep(2)
        
        raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")

# Example usage
if __name__ == "__main__":
    client = GitHubProtectionClient()
    
    # Example 1: Full protection workflow
    result = client.full_protection_workflow(
        github_url="https://github.com/example/repo",
        license_type="MIT"
    )
    
    print("Protection workflow started:", result['job_id'])
    
    # Wait for completion
    final_result = client.wait_for_job(result['job_id'])
    print("Workflow completed:", final_result['result'])
    
    # Example 2: Ask agent about security
    response = client.ask_agent(
        "What are the main security vulnerabilities I should look for in a Python web application?"
    )
    print("Agent response:", response['response'])
    
    # Example 3: Generate custom license
    license_result = client.generate_license(
        repo_type="machine learning library",
        usage_requirements="attribution required, no commercial use without permission"
    )
    print("Generated license:", license_result['license_text'])
\`;

// WebSocket Integration for Real-time Updates
const websocketIntegration = \`
// websocket-client.js
// Real-time updates for job status and violations

class GitHubProtectionWebSocket {
    constructor(wsUrl = 'ws://localhost:8000/ws') {
        this.wsUrl = wsUrl;
        this.ws = null;
        this.callbacks = {};
    }
    
    connect() {
        this.ws = new WebSocket(this.wsUrl);
        
        this.ws.onopen = () => {
            console.log('Connected to GitHub Protection Agent');
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        
        this.ws.onclose = () => {
            console.log('Disconnected from agent');
            // Reconnect after 5 seconds
            setTimeout(() => this.connect(), 5000);
        };
    }
    
    handleMessage(data) {
        const { type, payload } = data;
        
        switch (type) {
            case 'job_update':
                this.notifyCallbacks('job_update', payload);
                break;
            case 'violation_found':
                this.notifyCallbacks('violation_found', payload);
                break;
            case 'security_alert':
                this.notifyCallbacks('security_alert', payload);
                break;
        }
    }
    
    subscribe(event, callback) {
        if (!this.callbacks[event]) {
            this.callbacks[event] = [];
        }
        this.callbacks[event].push(callback);
    }
    
    notifyCallbacks(event, data) {
        if (this.callbacks[event]) {
            this.callbacks[event].forEach(callback => callback(data));
        }
    }
    
    subscribeToJob(jobId) {
        this.ws.send(JSON.stringify({
            type: 'subscribe_job',
            job_id: jobId
        }));
    }
}

// Usage example
const wsClient = new GitHubProtectionWebSocket();

wsClient.subscribe('job_update', (job) => {
    console.log('Job updated:', job);
    updateUI(job);
});

wsClient.subscribe('violation_found', (violation) => {
    console.log('Violation detected:', violation);
    showNotification('Code violation detected!', violation);
});

wsClient.connect();
\`;

// Smart Contract Deployment Script
const deploymentScript = \`
// deploy-contract.js
// Script to deploy the GitHub Protection smart contract

const { ethers } = require('hardhat');

async function main() {
    console.log('Deploying GitHubRepoProtection contract...');
    
    // Get the contract factory
    const GitHubRepoProtection = await ethers.getContractFactory('GitHubRepoProtection');
    
    // Deploy the contract
    const contract = await GitHubRepoProtection.deploy();
    await contract.deployed();
    
    console.log('Contract deployed to:', contract.address);
    console.log('Transaction hash:', contract.deployTransaction.hash);
    
    // Verify contract on Flow testnet (if verification is available)
    if (network.name !== 'hardhat') {
        console.log('Waiting for block confirmations...');
        await contract.deployTransaction.wait(6);
        
        console.log('Verifying contract...');
        try {
            await hre.run('verify:verify', {
                address: contract.address,
                constructorArguments: [],
            });
        } catch (error) {
            console.log('Verification failed:', error.message);
        }
    }
    
    // Save deployment info
    const deploymentInfo = {
        address: contract.address,
        network: network.name,
        deployer: (await ethers.getSigners())[0].address,
        blockNumber: contract.deployTransaction.blockNumber,
        transactionHash: contract.deployTransaction.hash,
        timestamp: new Date().toISOString()
    };
    
    require('fs').writeFileSync(
        'deployment.json',
        JSON.stringify(deploymentInfo, null, 2)
    );
    
    console.log('Deployment info saved to deployment.json');
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
\`;

export default GitHubProtectionDashboard;