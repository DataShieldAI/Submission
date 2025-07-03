from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import asyncio
import json
import os
import uuid
from datetime import datetime
import logging
from dotenv import load_dotenv


# Import our enhanced agent
from enhanced_agent_with_security import SimpleGitHubProtectionAgent as EnhancedGitHubProtectionAgent

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Enhanced GitHub Repository Protection API",
    description="AI-powered GitHub repository protection with comprehensive security auditing and blockchain integration",
    version="2.0.0"
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

# Enhanced Pydantic models
class RepositoryRegistration(BaseModel):
    github_url: HttpUrl
    license_type: str = "MIT"
    description: Optional[str] = None

class SecurityAuditRequest(BaseModel):
    github_url: HttpUrl
    audit_type: str = "comprehensive"
    include_private_keys: bool = True
    include_vulnerabilities: bool = True

class URLCleaningRequest(BaseModel):
    url_text: str

class ViolationReport(BaseModel):
    original_repo_id: int
    violating_url: HttpUrl
    similarity_score: float
    evidence_description: Optional[str] = None

class AgentQueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

class SecurityAuditResult(BaseModel):
    success: bool
    audit_id: Optional[int] = None
    files_scanned: Optional[int] = None
    total_findings: Optional[int] = None
    critical_findings: Optional[int] = None
    high_findings: Optional[int] = None
    medium_findings: Optional[int] = None
    ai_summary: Optional[str] = None
    error: Optional[str] = None

# In-memory job tracking
jobs = {}

@app.on_event("startup")
async def startup_event():
    """Initialize the enhanced agent on startup"""
    global agent
    
    config = {
        'USE_LOCAL_MODEL': os.getenv('USE_LOCAL_MODEL', 'false').lower() == 'true',
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN'),
        'CONTRACT_ADDRESS': os.getenv('CONTRACT_ADDRESS', '0x5fa19b4a48C20202055c8a6fdf16688633617D50')
    }
    
    # Check requirements
    if not config['USE_LOCAL_MODEL'] and not config['OPENAI_API_KEY']:
        logger.error("Missing OPENAI_API_KEY and USE_LOCAL_MODEL not set to true")
        raise RuntimeError("Please set OPENAI_API_KEY or USE_LOCAL_MODEL=true")
    
    try:
        agent = EnhancedGitHubProtectionAgent(config)
        logger.info("✅ Enhanced GitHub Protection Agent initialized successfully")
        
        if config['USE_LOCAL_MODEL']:
            logger.info("🦙 Using local model")
        else:
            logger.info("🤖 Using OpenAI GPT-4o-mini")
            
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        raise

@app.get("/")
async def root():
    """Enhanced health check endpoint"""
    ai_backend = "Local Model" if os.getenv('USE_LOCAL_MODEL') == 'true' else "OpenAI"
    openai_status = "✅ Available" if os.getenv('OPENAI_API_KEY') else "❌ No API key"
    
    return {
        "service": "Enhanced GitHub Repository Protection API",
        "version": "2.0.0",
        "status": "healthy",
        "agent_ready": agent is not None,
        "contract_address": os.getenv('CONTRACT_ADDRESS', '0x5fa19b4a48C20202055c8a6fdf16688633617D50'),
        "ai_backend": {
            "current": ai_backend,
            "openai": openai_status,
            "local_model": "✅ Enabled" if os.getenv('USE_LOCAL_MODEL') == 'true' else "❌ Disabled"
        },
        "database": "In-memory (no setup required)",
        "enhanced_features": [
            "Comprehensive security auditing",
            "Private key leak detection",
            "Vulnerability scanning",
            "URL cleaning and standardization",
            "Repository analysis and fingerprinting",
            "AI-powered violation detection",
            "Natural language agent interface",
            "Flow blockchain integration"
        ]
    }

@app.post("/clean-urls")
async def clean_github_urls(request: URLCleaningRequest) -> Dict:
    """Clean and standardize GitHub URLs from text input"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info("Cleaning GitHub URLs from text input")
        result = agent.clean_github_urls(request.url_text)
        
        return result
        
    except Exception as e:
        logger.error(f"URL cleaning failed: {e}")
        raise HTTPException(status_code=500, detail=f"URL cleaning failed: {str(e)}")

@app.post("/security-audit")
async def comprehensive_security_audit(request: SecurityAuditRequest) -> SecurityAuditResult:
    """Perform comprehensive security audit including private key detection"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info(f"Starting comprehensive security audit: {request.github_url}")
        result = agent.comprehensive_security_audit(str(request.github_url))
        
        return SecurityAuditResult(**result)
        
    except Exception as e:
        logger.error(f"Security audit failed: {e}")
        raise HTTPException(status_code=500, detail=f"Security audit failed: {str(e)}")

@app.get("/security-audit/{audit_id}")
async def get_security_audit(audit_id: int) -> Dict:
    """Get detailed security audit results"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    if audit_id not in agent.security_audits:
        raise HTTPException(status_code=404, detail="Security audit not found")
    
    return {
        "success": True,
        "audit": agent.security_audits[audit_id]
    }

@app.get("/security-audits")
async def list_security_audits() -> Dict:
    """List all security audits"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    return {
        "success": True,
        "total_audits": len(agent.security_audits),
        "audits": list(agent.security_audits.values())
    }

@app.post("/analyze-repository")
async def analyze_repository(request: RepositoryRegistration) -> Dict:
    """Analyze a GitHub repository for key features"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info(f"Analyzing repository: {request.github_url}")
        result = agent.analyze_repository(str(request.github_url))
        
        return result
        
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

@app.post("/full-protection-workflow")
async def full_protection_workflow(request: RepositoryRegistration) -> Dict:
    """Run complete protection workflow with enhanced security audit"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info(f"Starting enhanced protection workflow: {request.github_url}")
        result = agent.run_protection_workflow(str(request.github_url))
        
        return {
            "success": True,
            "workflow_result": result,
            "message": "Enhanced protection workflow completed with security audit"
        }
        
    except Exception as e:
        logger.error(f"Enhanced protection workflow failed: {e}")
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

@app.post("/agent-query")
async def agent_query(request: AgentQueryRequest) -> Dict:
    """Query the agent with natural language"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info(f"Agent query: {request.query}")
        
        # Add enhanced context
        enhanced_query = f"""
        You are an Enhanced GitHub Repository Protection Agent with comprehensive security auditing capabilities. 
        Help the user with:
        - Repository analysis and protection
        - Comprehensive security auditing (private keys, vulnerabilities)
        - License generation and compliance
        - Violation detection and DMCA notices
        - URL cleaning and standardization
        
        User query: {request.query}
        
        Current system status:
        - Repositories tracked: {len(agent.repositories)}
        - Violations found: {len(agent.violations)}
        - Security audits completed: {len(agent.security_audits)}
        - AI Backend: {'Local Model' if os.getenv('USE_LOCAL_MODEL') == 'true' else 'OpenAI'}
        """
        
        response = agent.agent.run(enhanced_query)
        
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

@app.get("/stats")
async def get_enhanced_stats() -> Dict:
    """Get enhanced system statistics"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    total_repos = len(agent.repositories)
    total_violations = len(agent.violations)
    total_audits = len(agent.security_audits)
    
    # Calculate security metrics
    critical_findings = 0
    high_findings = 0
    total_findings = 0
    
    for audit in agent.security_audits.values():
        if 'findings' in audit:
            findings = audit['findings']
            total_findings += len(findings)
            critical_findings += len([f for f in findings if f.get('severity') == 'critical'])
            high_findings += len([f for f in findings if f.get('severity') == 'high'])
    
    return {
        "success": True,
        "statistics": {
            "repositories": {
                "total_tracked": total_repos,
                "total_violations": total_violations,
                "protection_rate": f"{(total_repos / (total_repos + total_violations) * 100):.1f}%" if total_repos > 0 else "0%"
            },
            "security_audits": {
                "total_completed": total_audits,
                "total_findings": total_findings,
                "critical_findings": critical_findings,
                "high_findings": high_findings,
                "security_score": f"{max(0, 100 - (critical_findings * 10 + high_findings * 5)):.1f}%"
            }
        },
        "system_info": {
            "ai_backend": "Local Model" if os.getenv('USE_LOCAL_MODEL') == 'true' else "OpenAI",
            "database": "In-memory",
            "blockchain": "Flow Testnet",
            "enhanced_features": "Security Auditing Enabled"
        }
    }

@app.get("/agent-status")
async def get_agent_status() -> Dict:
    """Get enhanced agent status and capabilities"""
    if not agent:
        return {"status": "not_initialized", "capabilities": []}
    
    return {
        "status": "ready",
        "capabilities": [
            "repository_analysis",
            "code_fingerprinting", 
            "comprehensive_security_auditing",
            "private_key_leak_detection",
            "vulnerability_scanning",
            "violation_detection",
            "url_cleaning_and_standardization",
            "license_generation",
            "dmca_generation",
            "natural_language_interface"
        ],
        "tools_available": len(agent.tools),
        "memory_initialized": agent.memory is not None,
        "repositories_registered": len(agent.repositories),
        "violations_tracked": len(agent.violations),
        "security_audits_completed": len(agent.security_audits),
        "ai_backend": "Local Model" if os.getenv('USE_LOCAL_MODEL') == 'true' else "OpenAI",
        "contract_address": os.getenv('CONTRACT_ADDRESS'),
        "database": "In-memory (no external database required)",
        "enhanced_features": {
            "security_scanner": "✅ Active",
            "private_key_detection": "✅ Active",
            "vulnerability_scanning": "✅ Active",
            "url_cleaning": "✅ Active"
        }
    }

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

# Enhanced startup message
@app.on_event("startup")
async def startup_message():
    print("\n" + "="*70)
    print("🛡️  Enhanced GitHub Repository Protection Agent")
    print("="*70)
    print("✅ FastAPI Server Started")
    print(f"🤖 AI Backend: {'Local Model' if os.getenv('USE_LOCAL_MODEL') == 'true' else 'OpenAI'}")
    print("💾 Database: In-memory (no setup required)")
    print("🔗 Blockchain: Flow Testnet")
    print(f"📡 Contract: {os.getenv('CONTRACT_ADDRESS', '0x5fa19b4a48C20202055c8a6fdf16688633617D50')}")
    print("\n🔒 Enhanced Security Features:")
    print("   • Private key leak detection")
    print("   • Comprehensive vulnerability scanning")
    print("   • AI-powered security analysis")
    print("   • URL cleaning and standardization")
    print("\n🌐 API Available at: http://localhost:8000")
    print("📚 Docs Available at: http://localhost:8000/docs")
    print("="*70)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "enhanced_fastapi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )