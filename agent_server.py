from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import asyncio
import json
import os
import uuid
from datetime import datetime
import logging

# Import our agent
from github_protection_agent import GitHubProtectionAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GitHub Repository Protection API",
    description="AI-powered GitHub repository protection with blockchain integration",
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

class LicenseGenerationRequest(BaseModel):
    repo_type: str
    usage_requirements: str
    commercial_use: bool = True
    attribution_required: bool = True

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

# In-memory job tracking
jobs = {}

@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup"""
    global agent
    
    config = {
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN'),
        'PRIVATE_KEY': os.getenv('PRIVATE_KEY'),
        'CONTRACT_ADDRESS': os.getenv('CONTRACT_ADDRESS', '0x...')  # Replace with actual contract address
    }
    
    # Validate required environment variables
    required_vars = ['ANTHROPIC_API_KEY', 'GITHUB_TOKEN', 'PRIVATE_KEY']
    missing_vars = [var for var in required_vars if not config.get(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        raise RuntimeError(f"Missing environment variables: {missing_vars}")
    
    try:
        agent = GitHubProtectionAgent(config)
        logger.info("GitHub Protection Agent initialized successfully")
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
    return {
        "service": "GitHub Repository Protection API",
        "version": "1.0.0",
        "status": "healthy",
        "agent_ready": agent is not None
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
async def register_repository(
    request: RepositoryRegistration,
    background_tasks: BackgroundTasks
) -> JobResponse:
    """Register a repository for protection"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    job_id = create_job("register_repository", request.dict())
    
    async def registration_task():
        try:
            logger.info(f"Starting repository registration: {request.github_url}")
            result = agent.register_repository(
                str(request.github_url),
                request.license_type
            )
            update_job(job_id, "completed", result)
            logger.info(f"Repository registration completed: {job_id}")
        except Exception as e:
            logger.error(f"Repository registration failed: {e}")
            update_job(job_id, "failed", error=str(e))
    
    background_tasks.add_task(registration_task)
    
    return JobResponse(
        job_id=job_id,
        status="pending",
        message="Repository registration started",
        created_at=datetime.now().isoformat()
    )

@app.post("/security-audit")
async def security_audit(
    request: SecurityAuditRequest,
    background_tasks: BackgroundTasks
) -> JobResponse:
    """Perform security audit on repository"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    job_id = create_job("security_audit", request.dict())
    
    async def audit_task():
        try:
            logger.info(f"Starting security audit: {request.github_url}")
            result = agent.security_audit(str(request.github_url))
            update_job(job_id, "completed", result)
            logger.info(f"Security audit completed: {job_id}")
        except Exception as e:
            logger.error(f"Security audit failed: {e}")
            update_job(job_id, "failed", error=str(e))
    
    background_tasks.add_task(audit_task)
    
    return JobResponse(
        job_id=job_id,
        status="pending",
        message="Security audit started",
        created_at=datetime.now().isoformat()
    )

@app.post("/search-violations")
async def search_violations(
    repo_id: int,
    background_tasks: BackgroundTasks
) -> JobResponse:
    """Search for code violations"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    # First get repository details from blockchain
    try:
        # This would call the smart contract to get repo details
        # For now, using placeholder key features
        key_features = ["unique_algorithm", "custom_data_structure", "novel_implementation"]
        
        job_id = create_job("search_violations", {"repo_id": repo_id})
        
        async def search_task():
            try:
                logger.info(f"Searching for violations: repo {repo_id}")
                violations = agent.search_for_violations(repo_id, key_features)
                update_job(job_id, "completed", violations)
                logger.info(f"Violation search completed: {job_id}")
            except Exception as e:
                logger.error(f"Violation search failed: {e}")
                update_job(job_id, "failed", error=str(e))
        
        background_tasks.add_task(search_task)
        
        return JobResponse(
            job_id=job_id,
            status="pending",
            message="Violation search started",
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to start violation search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/report-violation")
async def report_violation(request: ViolationReport) -> Dict:
    """Report a code violation to blockchain"""
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
            result['dmca_generated'] = dmca_result
        
        return result
        
    except Exception as e:
        logger.error(f"Violation reporting failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-license")
async def generate_license(request: LicenseGenerationRequest) -> Dict:
    """Generate appropriate license for repository"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info(f"Generating license for {request.repo_type}")
        license_text = agent.generate_license(
            request.repo_type,
            request.usage_requirements
        )
        
        return {
            "success": True,
            "license_text": license_text,
            "repo_type": request.repo_type,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"License generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/full-protection-workflow")
async def full_protection_workflow(
    request: RepositoryRegistration,
    background_tasks: BackgroundTasks
) -> JobResponse:
    """Run complete protection workflow"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    job_id = create_job("full_workflow", request.dict())
    
    async def workflow_task():
        try:
            logger.info(f"Starting full protection workflow: {request.github_url}")
            result = agent.run_protection_workflow(str(request.github_url))
            update_job(job_id, "completed", result)
            logger.info(f"Full protection workflow completed: {job_id}")
        except Exception as e:
            logger.error(f"Full protection workflow failed: {e}")
            update_job(job_id, "failed", error=str(e))
    
    background_tasks.add_task(workflow_task)
    
    return JobResponse(
        job_id=job_id,
        status="pending",
        message="Full protection workflow started",
        created_at=datetime.now().isoformat()
    )

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

@app.get("/job/{job_id}")
async def get_job_status(job_id: str) -> Dict:
    """Get job status and results"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]

@app.get("/jobs")
async def list_jobs(limit: int = 50) -> List[Dict]:
    """List all jobs"""
    sorted_jobs = sorted(
        jobs.values(),
        key=lambda x: x['created_at'],
        reverse=True
    )
    return sorted_jobs[:limit]

@app.delete("/job/{job_id}")
async def delete_job(job_id: str) -> Dict:
    """Delete a job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    del jobs[job_id]
    return {"message": "Job deleted successfully"}

@app.get("/contract-info")
async def get_contract_info() -> Dict:
    """Get smart contract information"""
    return {
        "contract_address": os.getenv('CONTRACT_ADDRESS'),
        "network": "Flow Testnet",
        "chain_id": 545,
        "rpc_url": "https://testnet.evm.nodes.onflow.org"
    }

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
            "blockchain_integration"
        ],
        "tools_available": len(agent.tools),
        "memory_initialized": agent.memory is not None
    }

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return {
        "error": "Internal server error",
        "message": str(exc),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "agent_fastapi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )