from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import sys
from app.context_builder.builder import ContextBuilder
from app.schemas.infra_schema import InfraSummary
from app.ai.orchestrator import AIOrchestrator
from app.diagrams.mermaid import MermaidGenerator
from app.core.config import GROQ_API_KEY

app = FastAPI(
    title="InfraMind API",
    description="Backend API for InfraMind - AI Infrastructure Intelligence",
    version="0.1.0",
)

@app.on_event("startup")
def startup_event():
    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY missing.", file=sys.stderr)
        print("Please configure your .env file.", file=sys.stderr)
        sys.exit(1)


class ParseRequest(BaseModel):
    directory_path: str

class AIReviewResponse(BaseModel):
    result: str

class DiagramResponse(BaseModel):
    mermaid: str

@app.get("/")
def read_root():
    return {"message": "Welcome to InfraMind API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/parse", response_model=InfraSummary)
def parse_infrastructure(request: ParseRequest):
    if not os.path.exists(request.directory_path) or not os.path.isdir(request.directory_path):
        raise HTTPException(status_code=400, detail="Invalid directory path")
        
    try:
        builder = ContextBuilder(request.directory_path)
        summary = builder.build_context()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing infrastructure: {str(e)}")

@app.post("/api/v1/diagram", response_model=DiagramResponse)
def generate_diagram(request: ParseRequest):
    if not os.path.exists(request.directory_path) or not os.path.isdir(request.directory_path):
        raise HTTPException(status_code=400, detail="Invalid directory path")
        
    try:
        builder = ContextBuilder(request.directory_path)
        summary = builder.build_context()
        generator = MermaidGenerator(summary.resources, summary.dependencies)
        mermaid_code = generator.generate()
        return DiagramResponse(mermaid=mermaid_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating diagram: {str(e)}")

@app.post("/api/v1/explain", response_model=AIReviewResponse)
def explain_infrastructure(request: ParseRequest):
    if not os.path.exists(request.directory_path) or not os.path.isdir(request.directory_path):
        raise HTTPException(status_code=400, detail="Invalid directory path")
    
    try:
        builder = ContextBuilder(request.directory_path)
        summary = builder.build_context()
        orchestrator = AIOrchestrator()
        result = orchestrator.explain_infrastructure(summary)
        return AIReviewResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error explaining infrastructure: {str(e)}")

@app.post("/api/v1/security-review", response_model=AIReviewResponse)
def security_review(request: ParseRequest):
    if not os.path.exists(request.directory_path) or not os.path.isdir(request.directory_path):
        raise HTTPException(status_code=400, detail="Invalid directory path")
    
    try:
        builder = ContextBuilder(request.directory_path)
        summary = builder.build_context()
        orchestrator = AIOrchestrator()
        result = orchestrator.review_security(summary)
        return AIReviewResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reviewing security: {str(e)}")

@app.post("/api/v1/cost-review", response_model=AIReviewResponse)
def cost_review(request: ParseRequest):
    if not os.path.exists(request.directory_path) or not os.path.isdir(request.directory_path):
        raise HTTPException(status_code=400, detail="Invalid directory path")
    
    try:
        builder = ContextBuilder(request.directory_path)
        summary = builder.build_context()
        orchestrator = AIOrchestrator()
        result = orchestrator.review_cost(summary)
        return AIReviewResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reviewing costs: {str(e)}")
