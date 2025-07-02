from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import asyncio
import json
import os
import uuid
from datetime import datetime
import logging

# Import our simplified agent
from simplified_agent import SimpleGitHubProtectionAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GitHub Repository Protection API (Simplified)",
    description="AI-powered GitHub repository protection with blockchain integration - No database required!",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent = None

# Pydantic models
class RepositoryRegistration(BaseModel):
    github_url: HttpUrl
    license_type: str = "MIT"
    description: Optional[str] = None

class ViolationReport(BaseModel):
    original_repo_id: int
    violating_url: HttpUrl
    similarity_score: float
    evidence_description: Optional[str] = None

class SecurityAuditRequest(BaseModel):
    github_url: HttpUrl
    audit_type: str = "comprehensive"

class AgentQueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str
    created_at: str

class AnalysisResult(BaseModel):
    success: bool
    repo_hash: Optional[str] = None
    fingerprint: Optional[str] = None
    key_features: Optional[str] = None
    total_files: Optional[int] = None
    error: Optional[str] = None

# In-memory job tracking (no database needed)
jobs = {}

@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup"""
    global agent
    
    config = {
        'USE_OLLAMA': os.getenv('USE_OLLAMA', 'false').lower() == 'true',
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN'),
        'CONTRACT_ADDRESS': os.getenv('CONTRACT_ADDRESS', '0x5fa19b4a48C20202055c8a6fdf16688633617D50')
    }
    
    # Check requirements
    if not config['USE_OLLAMA'] and not config['OPENAI_API_KEY']:
        logger.error("Missing OPENAI_API_KEY and USE_OLLAMA not set to true")
        raise RuntimeError("Please set OPENAI_API_KEY or USE_OLLAMA=true")
    
    try:
        agent = SimpleGitHubProtectionAgent(config)
        logger.info("✅ GitHub Protection Agent initialized successfully")
        
        if config['USE_OLLAMA']:
            logger.info("🦙 Using Ollama (free local model)")
        else:
            logger.info("🤖 Using OpenAI GPT-4o-mini")
            
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        raise

def create_job(job_type: str, data: Dict) -> str:
    """Create a new background job"""
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        'id': job_id,
        'type': job_type,
        'status': 'pending',
        'data': data,
        'result': None,
        'error': None,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    return job_id

def update_job(job_id: str, status: str, result: Any = None, error: str = None):
    """Update job status"""
    if job_id in jobs:
        jobs[job_id].update({
            'status': status,
            'result': result,
            'error': error,
            'updated_at': datetime.now().isoformat()
        })

@app.get("/")
async def root():
    """Health check endpoint"""
    ollama_status = "✅ Connected" if os.getenv('USE_OLLAMA') == 'true' else "❌ Not using Ollama"
    openai_status = "✅ Available" if os.getenv('OPENAI_API_KEY') else "❌ No API key"
    
    return {
        "service": "GitHub Repository Protection API (Simplified)",
        "version": "1.0.0",
        "status": "healthy",
        "agent_ready": agent is not None,
        "contract_address": os.getenv('CONTRACT_ADDRESS', '0x5fa19b4a48C20202055c8a6fdf16688633617D50'),
        "ai_backend": {
            "ollama": ollama_status,
            "openai": openai_status
        },
        "database": "In-memory (no setup required)",
        "features": [
            "Repository analysis and fingerprinting",
            "AI-powered security auditing",
            "GitHub violation detection",
            "Natural language agent interface",
            "Flow blockchain integration",
            "Zero database setup"
        ]
    }

@app.post("/analyze-repository")
async def analyze_repository(request: RepositoryRegistration) -> AnalysisResult:
    """Analyze a GitHub repository"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info(f"Analyzing repository: {request.github_url}")
        result = agent.analyze_repository(str(request.github_url))
        
        return AnalysisResult(**result)
        
    except Exception as e:
        logger.error(f"Repository analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/register-repository")
async def register_repository(request: RepositoryRegistration) -> Dict:
    """Register a repository for protection"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info(f"Registering repository: {request.github_url}")
        result = agent.register_repository(
            str(request.github_url),
            request.license_type
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Repository registration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/security-audit")
async def security_audit(request: SecurityAuditRequest) -> Dict:
    """Perform security audit on repository"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info(f"Starting security audit: {request.github_url}")
        result = agent.security_audit(str(request.github_url))
        
        return result
        
    except Exception as e:
        logger.error(f"Security audit failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search-violations/{repo_id}")
async def search_violations(repo_id: int) -> Dict:
    """Search for code violations"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info(f"Searching for violations: repo {repo_id}")
        violations = agent.search_for_violations(repo_id)
        
        return {
            "success": True,
            "repo_id": repo_id,
            "violations_found": len(violations),
            "violations": violations
        }
        
    except Exception as e:
        logger.error(f"Violation search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/report-violation")
async def report_violation(request: ViolationReport) -> Dict:
    """Report a code violation"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info(f"Reporting violation: {request.violating_url}")
        result = agent.report_violation(
            request.original_repo_id,
            str(request.violating_url),
            request.similarity_score
        )
        
        # Generate DMCA if violation reported successfully
        if result.get('success'):
            dmca_result = agent.generate_dmca({
                'violating_url': str(request.violating_url),
                'similarity_score': request.similarity_score,
                'evidence_hash': result.get('evidence_hash'),
                'tx_hash': result.get('tx_hash')
            })
            result['dmca_notice'] = dmca_result
        
        return result
        
    except Exception as e:
        logger.error(f"Violation reporting failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/full-protection-workflow")
async def full_protection_workflow(request: RepositoryRegistration) -> Dict:
    """Run complete protection workflow"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info(f"Starting full protection workflow: {request.github_url}")
        result = agent.run_protection_workflow(str(request.github_url))
        
        return {
            "success": True,
            "workflow_result": result,
            "message": "Protection workflow completed"
        }
        
    except Exception as e:
        logger.error(f"Full protection workflow failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent-query")
async def agent_query(request: AgentQueryRequest) -> Dict:
    """Query the agent with natural language"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info(f"Agent query: {request.query}")
        
        # Use the agent's LangChain agent to process the query
        response = agent.agent.run(request.query)
        
        return {
            "success": True,
            "response": response,
            "query": request.query,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Agent query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/repositories")
async def list_repositories() -> Dict:
    """List all registered repositories"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return {
        "success": True,
        "total_repositories": len(agent.repositories),
        "repositories": list(agent.repositories.values())
    }

@app.get("/violations")
async def list_violations() -> Dict:
    """List all reported violations"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return {
        "success": True,
        "total_violations": len(agent.violations),
        "violations": list(agent.violations.values())
    }

@app.get("/repository/{repo_id}")
async def get_repository(repo_id: int) -> Dict:
    """Get repository details"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    if repo_id not in agent.repositories:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    return {
        "success": True,
        "repository": agent.repositories[repo_id]
    }

@app.get("/violation/{violation_id}")
async def get_violation(violation_id: int) -> Dict:
    """Get violation details"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    if violation_id not in agent.violations:
        raise HTTPException(status_code=404, detail="Violation not found")
    
    return {
        "success": True,
        "violation": agent.violations[violation_id]
    }

@app.post("/generate-dmca/{violation_id}")
async def generate_dmca_notice(violation_id: int) -> Dict:
    """Generate DMCA notice for a specific violation"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    if violation_id not in agent.violations:
        raise HTTPException(status_code=404, detail="Violation not found")
    
    try:
        violation = agent.violations[violation_id]
        dmca_notice = agent.generate_dmca(violation)
        
        return {
            "success": True,
            "violation_id": violation_id,
            "dmca_notice": dmca_notice,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"DMCA generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent-status")
async def get_agent_status() -> Dict:
    """Get agent status and capabilities"""
    if not agent:
        return {"status": "not_initialized", "capabilities": []}
    
    return {
        "status": "ready",
        "capabilities": [
            "repository_analysis",
            "code_fingerprinting", 
            "violation_detection",
            "security_auditing",
            "license_generation",
            "dmca_generation",
            "natural_language_interface"
        ],
        "tools_available": len(agent.tools),
        "memory_initialized": agent.memory is not None,
        "repositories_registered": len(agent.repositories),
        "violations_tracked": len(agent.violations),
        "ai_backend": "Ollama" if os.getenv('USE_OLLAMA') == 'true' else "OpenAI",
        "contract_address": os.getenv('CONTRACT_ADDRESS'),
        "database": "In-memory (no external database required)"
    }

@app.get("/stats")
async def get_stats() -> Dict:
    """Get system statistics"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    total_repos = len(agent.repositories)
    total_violations = len(agent.violations)
    
    # Calculate some basic stats
    pending_violations = sum(1 for v in agent.violations.values() if v.get('status') == 'pending')
    
    return {
        "success": True,
        "statistics": {
            "total_repositories": total_repos,
            "total_violations": total_violations,
            "pending_violations": pending_violations,
            "resolved_violations": total_violations - pending_violations,
            "protection_rate": f"{(total_repos / (total_repos + total_violations) * 100):.1f}%" if total_repos > 0 else "0%"
        },
        "system_info": {
            "ai_backend": "Ollama (Local)" if os.getenv('USE_OLLAMA') == 'true' else "OpenAI",
            "database": "In-memory",
            "blockchain": "Flow Testnet"
        }
    }

@app.delete("/repository/{repo_id}")
async def delete_repository(repo_id: int) -> Dict:
    """Delete a repository (remove from tracking)"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    if repo_id not in agent.repositories:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    repo = agent.repositories.pop(repo_id)
    
    return {
        "success": True,
        "message": f"Repository {repo['github_url']} removed from tracking",
        "deleted_repo": repo
    }

@app.post("/chat")
async def chat_with_agent(request: AgentQueryRequest) -> Dict:
    """Interactive chat interface with the agent"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Add some context to make responses more helpful
        enhanced_query = f"""
        You are a GitHub Repository Protection Agent. Help the user with:
        - Repository analysis and protection
        - Security auditing
        - License generation
        - Violation detection and DMCA notices
        
        User query: {request.query}
        
        Current system status:
        - Repositories tracked: {len(agent.repositories)}
        - Violations found: {len(agent.violations)}
        - AI Backend: {'Ollama (Local)' if os.getenv('USE_OLLAMA') == 'true' else 'OpenAI'}
        """
        
        response = agent.agent.run(enhanced_query)
        
        return {
            "success": True,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "conversation_context": {
                "repositories_tracked": len(agent.repositories),
                "violations_found": len(agent.violations)
            }
        }
        
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return {
        "error": "Internal server error",
        "message": str(exc),
        "timestamp": datetime.now().isoformat()
    }

# Startup message
@app.on_event("startup")
async def startup_message():
    print("\n" + "="*60)
    print("🛡️  GitHub Repository Protection Agent")
    print("="*60)
    print("✅ FastAPI Server Started")
    print(f"🤖 AI Backend: {'Ollama (Free)' if os.getenv('USE_OLLAMA') == 'true' else 'OpenAI'}")
    print("💾 Database: In-memory (no setup required)")
    print("🔗 Blockchain: Flow Testnet")
    print(f"📡 Contract: {os.getenv('CONTRACT_ADDRESS', '0x5fa19b4a48C20202055c8a6fdf16688633617D50')}")
    print("\n🌐 API Available at: http://localhost:8000")
    print("📚 Docs Available at: http://localhost:8000/docs")
    print("="*60)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "simple_fastapi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )