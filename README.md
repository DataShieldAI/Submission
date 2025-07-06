# GitHub Repository Protection Agent

**An AI agent that leverages the Flow blockchain to provide immutable ownership verification and automated IP protection for developers.**

---

## 🚀 Overview

This project is an advanced AI agent that helps developers protect their GitHub repositories from unauthorized use. The system combines powerful AI analysis with the security and immutability of the **Flow blockchain**, which acts as the core trust layer for all operations. By creating an on-chain record of code ownership, the agent can confidently and automatically monitor for theft, generate legal notices, and safeguard intellectual property.

---

## 💼 Value Proposition

In today's open-source world, protecting software IP is a significant challenge. This project addresses these pain points by leveraging the unique advantages of the Flow blockchain:

* **Automated Vigilance**: The AI agent automates discovery and evidence collection, replacing expensive manual oversight and allowing developers to focus on building.
* **Irrefutable Proof of Ownership on Flow**: By registering code fingerprints on the **Flow blockchain**, we provide irrefutable, timestamped proof of ownership. This significantly strengthens DMCA claims and other legal actions by grounding them in on-chain truth.
* **Incentivized Community Monitoring**: The system is designed to support an incentive model on Flow. By offering token-based incentives to a community of users who find and flag infringing repositories, the platform can scale its monitoring efforts far beyond what a single company could achieve.
* **Valuable Developer Tools**: Beyond protection, the agent provides high-value utilities like the **Extensive Security Auditor**, which is a powerful tool for any development team to secure their codebase.

---

## 🌊 Built on Flow: Deep Integration

This project isn't just using a blockchain; it's an **AI agent powered by Flow**. Flow serves as the fundamental source of truth that enables the agent to act with authority.

* **The Trust Layer for AI**: The AI agent's most critical actions, such as generating a DMCA notice, are directly informed by verifiable data on the Flow blockchain. Before taking action against a potential copy, the agent first queries our smart contract on Flow to confirm the original repository's ownership and registration date. This prevents errors and adds weight to every action taken.

* **Smart Contract on Flow EVM**: Our Solidity smart contract is deployed to the **Flow EVM Testnet** and handles the core logic for IP management. Key functions like `registerRepository` and `reportViolation` create a permanent, auditable, and tamper-proof log of all protected assets and enforcement actions.

* **Seamless Frontend with FCL**: The user-facing dApp utilizes the **Flow Client Library (FCL)**. This allows developers to connect their favorite Flow wallets (like Lilico or Blocto) with a familiar and secure workflow to register their repositories, pay for gas, and manage their protected assets directly on Flow.

* **Backend & Agent Integration**: The core Python agent communicates directly with the deployed smart contract. It uses the contract as its source of truth to validate claims and writes new violation records to the chain, bridging the gap between off-chain AI analysis and on-chain verification.

---

## ✨ Key Features

### 🔍 **Intelligent Code Analysis**
* **Repository Fingerprinting**: Generates unique signatures for code repositories using AI.
* **Key Feature Extraction**: Identifies distinctive algorithms, patterns, and implementations.
* **Security Auditing**: Automated security vulnerability detection, including a deep scan of the entire commit history.
* **License Generation**: AI-powered license creation, including a custom AI-restrictive license.

### 🛡️ **Blockchain Protection on Flow**
* **Ownership Registration**: Records repository ownership on the **Flow blockchain**.
* **Immutable Proof**: Cryptographic evidence of code authorship and creation time, secured by Flow.
* **Violation Tracking**: On-chain records of code theft and unauthorized usage.
* **IPFS Integration**: Uploads licenses and DMCA notices to IPFS for decentralized storage, with the hash pinned on Flow.

### 🤖 **AI-Powered Monitoring**
* **Similarity Detection**: Advanced algorithms to find copied code across GitHub.
* **Automated Scanning**: Continuous monitoring for potential violations, guided by on-chain data.
* **Evidence Collection**: Automatic gathering of proof for copyright claims.
* **Automated DMCA Generation**: AI-generated legal takedown notices in professionally formatted PDF documents.

---

## 🏗️ Architecture


┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub API    │    │  LlamaIndex      │    │  Flow Blockchain │
│   Repository    │◄──►│  Code Analysis   │◄──►│  (Source of Truth) │
│   Scanning      │    │  & Similarity    │    │  Smart Contract  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
│                        │                        │
└────────────────────────┼────────────────────────┘
│
┌─────────────────────────▼─────────────────────────┐
│              LangChain Agent                      │
│ (Acts based on data verified on the Flow Blockchain) │
│        ┌──────────────────────────────────┐       │
│        │  • Repository Registration       │       │
│        │  • Violation Detection           │       │
│        │  • Security Auditing             │       │
│        │  • DMCA Creation                 │       │
│        └──────────────────────────────────┘       │
└───────────────────────────────────────────────────┘



---

## 🛠️ Technology Stack

* **AI/ML**: LangChain, LlamaIndex, Anthropic Claude, Sentence Transformers
* **Blockchain**: **Flow EVM**, **Flow Client Library (FCL)**, Solidity, AgentKit, Viem
* **Backend**: FastAPI, Python, PostgreSQL, Redis
* **Frontend**: React, Next.js, TailwindCSS
* **DevOps**: Docker, Kubernetes, GitHub Actions

---

## 🚀 Quick Start

### Prerequisites
* Python 3.11+
* Node.js 18+
* A Flow wallet with testnet FLOW tokens to interact with the dApp.

### Environment Setup

```bash
# Clone repository
git clone [https://github.com/your-org/github-protection-agent](https://github.com/your-org/github-protection-agent)
cd github-protection-agent

# Install Python dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your API keys. The contract is already deployed for you!
vim .env
```
Required environment variables:
```bash
ANTHROPIC_API_KEY=your_anthropic_api_key
GITHUB_TOKEN=your_github_token
PRIVATE_KEY=your_flow_wallet_private_key # Required for the agent to submit transactions
# The smart contract is already deployed on Flow Testnet at the address below:
CONTRACT_ADDRESS=0x5fa19b4a48C20202055c8a6fdf16688633617D50
```

## Start the Agent
You can run the agent in two modes:

1. Run Full Backend Server
This exposes all the API endpoints for a frontend application or programmatic use.
```bash
# Run the FastAPI server
python enhanced_fastapi_server_with_security.py
```
The API will be available at http://localhost:8000.

2. Run Interactive CLI Playground
This allows you to directly interact with the agent's features from your terminal.
```bash
# Run the command-line playground
python main_enhanced.py
```

### 📖 Usage Examples (CLI Playground)
The following examples demonstrate how to use the agent via the interactive playground (main_enhanced.py).

1. Compare Two Repositories
Analyzes two repositories for similarity, a crucial step when investigating a potential DMCA claim.
```bash
analyze [github.com/facebook/react](https://github.com/facebook/react) [https://github.com/preactjs/preact](https://github.com/preactjs/preact)
```

2. Run a Comprehensive Security Audit
Scans a repository for exposed API keys and other secrets. The --extensive flag checks every file across every commit in the repository's history.
```bash
# Run an extensive audit on the Express.js repository
audit [https://github.com/expressjs/express](https://github.com/expressjs/express) --extensive
```


3. Scan for Violations and Generate DMCA Notice
Scans GitHub for code infringing upon a repository registered on Flow and automatically generates a PDF DMCA notice.
```bash
# Scan for violations of a registered repo with ID 1
scan 1
```

4. Run the Full Protection Workflow
Executes the complete end-to-end workflow: analysis, security audit, license PDF generation, IPFS pinning, and blockchain registration on Flow.
```bash
# Onboard and protect a new repository on Flow
workflow [https://github.com/your-username/your-awesome-project](https://github.com/your-username/your-awesome-project)
```


## 🔐 Smart Contract Functions
The core logic deployed on the Flow EVM.

Repository Management
```solidity
function registerRepository(
    string memory githubUrl,
    string memory repoHash,
    string memory codeFingerprint,
    string[] memory keyFeatures,
    string memory licenseType,
    string memory ipfsMetadata
) external returns (uint256);
```

Violation Reporting
```solidity
function reportViolation(
    uint256 originalRepoId,
    string memory violatingUrl,
    string memory evidenceHash,
    uint256 similarityScore
) external returns (uint256);
```


## 🙏 Acknowledgments
- Flow Blockchain for providing a fast, scalable, and developer-friendly platform for building decentralized applications.
- LangChain & LlamaIndex for the powerful agent and data frameworks.


### Team:


Telegram: @P_Pwoo
Discord: ppwoo


Jamie Jamerson 