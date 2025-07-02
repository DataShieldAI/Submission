# GitHub Repository Protection Agent

**AI-powered repository protection with blockchain-based ownership verification and automated DMCA generation.**

## 🚀 Overview

This project creates an advanced AI agent that helps developers protect their GitHub repositories from unauthorized copying and usage. The system combines LLamaIndex for intelligent code analysis, LangChain for natural language processing, and Flow blockchain for immutable ownership records.

## ✨ Key Features

### 🔍 **Intelligent Code Analysis**
- **Repository Fingerprinting**: Generates unique signatures for code repositories using AI
- **Key Feature Extraction**: Identifies distinctive algorithms, patterns, and implementations
- **Security Auditing**: Automated security vulnerability detection and reporting
- **License Generation**: AI-powered license creation based on usage requirements

### 🛡️ **Blockchain Protection**
- **Ownership Registration**: Record repository ownership on Flow blockchain
- **Immutable Proof**: Cryptographic evidence of code authorship and creation time
- **Violation Tracking**: On-chain records of code theft and unauthorized usage
- **Dispute Resolution**: Blockchain-based dispute and resolution system

### 🤖 **AI-Powered Monitoring**
- **Similarity Detection**: Advanced algorithms to find copied code across GitHub
- **Automated Scanning**: Continuous monitoring for potential violations
- **Evidence Collection**: Automatic gathering of proof for copyright claims
- **DMCA Generation**: AI-generated legal takedown notices

### 🔗 **Flow Blockchain Integration**
- **EVM Compatibility**: Uses Flow's EVM for smart contract deployment
- **Low Transaction Costs**: Efficient blockchain operations
- **AgentKit Integration**: Seamless wallet and transaction management
- **Native VRF**: Secure randomness for verification processes

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub API    │    │  LlamaIndex      │    │  Flow Blockchain │
│   Repository    │◄──►│  Code Analysis   │◄──►│  Smart Contract  │
│   Scanning      │    │  & Similarity    │    │  Ownership       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                 │
         ┌─────────────────────────▼─────────────────────────┐
         │              LangChain Agent                      │
         │           Natural Language Interface              │
         │        ┌──────────────────────────────────┐       │
         │        │  • Repository Registration       │       │
         │        │  • Violation Detection           │       │
         │        │  • Security Auditing             │       │
         │        │  • License Generation            │       │
         │        │  • DMCA Creation                 │       │
         │        └──────────────────────────────────┘       │
         └───────────────────────────────────────────────────┘
```

## 🛠️ Technology Stack

- **AI/ML**: LangChain, LlamaIndex, Anthropic Claude, Sentence Transformers
- **Blockchain**: Flow EVM, Solidity, AgentKit, Viem
- **Backend**: FastAPI, Python, PostgreSQL, Redis
- **Frontend**: React, Next.js, TailwindCSS
- **DevOps**: Docker, Kubernetes, GitHub Actions

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Flow wallet with testnet FLOW tokens

### Environment Setup

```bash
# Clone repository
git clone https://github.com/your-org/github-protection-agent
cd github-protection-agent

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
vim .env
```

Required environment variables:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key
GITHUB_TOKEN=your_github_token
PRIVATE_KEY=your_flow_wallet_private_key
CONTRACT_ADDRESS=deployed_contract_address
```

### Deploy Smart Contract

```bash
# Install dependencies
npm install

# Deploy to Flow testnet
npx hardhat run scripts/deploy.js --network flow-testnet

# Note the contract address for your .env file
```

### Start the Agent

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Or run locally
pip install -r requirements.txt
uvicorn agent_fastapi_server:app --reload
```

The agent will be available at `http://localhost:8000`

## 📖 Usage Examples

### 1. Register Repository

```python
from github_protection_sdk import GitHubProtectionClient

client = GitHubProtectionClient()

# Register repository for protection
result = client.register_repository(
    github_url="https://github.com/username/my-project",
    license_type="MIT"
)

print(f"Registration job: {result['job_id']}")

# Wait for completion
final_result = client.wait_for_job(result['job_id'])
print(f"Repository registered with hash: {final_result['result']['repo_hash']}")
```

### 2. Security Audit

```python
# Perform comprehensive security audit
audit_result = client.security_audit(
    github_url="https://github.com/username/my-project"
)

# Get audit results
audit_job = client.wait_for_job(audit_result['job_id'])
print("Security findings:", audit_job['result']['audit_result'])
```

### 3. Natural Language Queries

```python
# Ask the agent questions
response = client.ask_agent(
    "What are the main security vulnerabilities in my Python Flask application?"
)

print("Agent advice:", response['response'])
```

### 4. Violation Detection

```python
# Search for potential code theft
violations = client.search_violations(repo_id=1)

# Report violations found
for violation in violations['result']:
    if violation['similarity'] > 0.8:
        client.report_violation(
            original_repo_id=1,
            violating_url=violation['repo_url'],
            similarity_score=violation['similarity']
        )
```

## 🔧 API Endpoints

### Core Operations
- `POST /register-repository` - Register repository for protection
- `POST /security-audit` - Perform security audit
- `POST /search-violations/{repo_id}` - Search for code violations
- `POST /report-violation` - Report code theft to blockchain
- `POST /generate-license` - Generate appropriate license

### Agent Interaction
- `POST /agent-query` - Natural language queries
- `POST /full-protection-workflow` - Complete protection setup

### Job Management
- `GET /job/{job_id}` - Get job status
- `GET /jobs` - List all jobs
- `DELETE /job/{job_id}` - Delete job

### Utilities
- `GET /contract-info` - Smart contract information
- `GET /agent-status` - Agent health and capabilities

## 🔐 Smart Contract Functions

### Repository Management
```solidity
function registerRepository(
    string memory githubUrl,
    string memory repoHash,
    string memory codeFingerprint,
    string[] memory keyFeatures,
    string memory licenseType,
    string memory ipfsMetadata
) external returns (uint256)
```

### Violation Reporting
```solidity
function reportViolation(
    uint256 originalRepoId,
    string memory violatingUrl,
    string memory evidenceHash,
    uint256 similarityScore
) external returns (uint256)
```

### Status Updates
```solidity
function updateViolationStatus(
    uint256 violationId,
    ViolationStatus newStatus,
    string memory dmcaReference
) external
```

## 🚦 Deployment

### Docker Deployment
```bash
# Build and deploy
docker-compose up -d

# Scale for production
docker-compose up -d --scale agent-api=3
```

### Kubernetes Deployment
```bash
# Apply configurations
kubectl apply -f k8s-deployment.yaml

# Check status
kubectl get pods -l app=github-protection-agent
```

### Environment-Specific Configs
- **Development**: Local Docker setup with hot reload
- **Staging**: Kubernetes cluster with Flow testnet
- **Production**: Multi-region deployment with Flow mainnet

## 🔍 Monitoring & Observability

### Health Checks
- **API Health**: `GET /` endpoint
- **Agent Status**: `GET /agent-status`
- **Database**: PostgreSQL connection monitoring
- **Blockchain**: Flow network connectivity

### Metrics Collection
- Request/response times
- Job completion rates
- Violation detection accuracy
- Smart contract gas usage

### Logging
- Structured JSON logging
- Centralized log aggregation
- Error tracking and alerting

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Code formatting
black github_protection_agent.py
flake8 github_protection_agent.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Flow Blockchain** for EVM compatibility and low-cost transactions
- **Anthropic** for Claude AI capabilities
- **LangChain** for agent framework
- **LlamaIndex** for intelligent document processing

## 🔗 Links

- **Live Demo**: [https://github-protection.flow.com](https://github-protection.flow.com)
- **Documentation**: [https://docs.github-protection.flow.com](https://docs.github-protection.flow.com)
- **Flow Developer Portal**: [https://developers.flow.com](https://developers.flow.com)
- **Contract Address**: `0x...` (Flow Testnet)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/github-protection-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/github-protection-agent/discussions)
- **Discord**: [Flow Discord](https://discord.gg/flow)

---

