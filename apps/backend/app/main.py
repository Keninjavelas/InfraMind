import asyncio
import os
import sys
from typing import Any, List, Optional

from app.ai.orchestrator import AIOrchestrator
from app.context_builder.builder import ContextBuilder
from app.core.config import GROQ_API_KEY
from app.diagrams.mermaid import MermaidGenerator
from app.schemas.infra_schema import (
    ComplexityMetrics,
    Dependency,
    InfraSummary,
    Resource,
    SecurityRisk,
)
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Initialize slowapi rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="InfraMind API",
    description="Backend API for InfraMind - AI Infrastructure Intelligence",
    version="0.1.0",
)

app.state.limiter = limiter


# Custom rate limit exception handler to yield a graceful fallback response
@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    try:
        body = await request.json()
        directory_path = body.get("directory_path")
        if (
            directory_path
            and os.path.exists(directory_path)
            and os.path.isdir(directory_path)
        ):
            builder = ContextBuilder(directory_path)
            summary = builder.build_context()
            return JSONResponse(
                status_code=200,
                content={
                    "result": "AI reasoning is currently unavailable due to rate limits.",
                    "status": "fallback",
                    "message": "AI reasoning unavailable.",
                    "deterministic_analysis_available": True,
                    "services": summary.services,
                    "resources": [r.model_dump() for r in summary.resources],
                    "dependencies": [d.model_dump() for d in summary.dependencies],
                    "security_risks": [
                        sr.model_dump() for sr in summary.security_risks
                    ],
                    "metrics": summary.metrics.model_dump(),
                    "estimated_complexity": summary.estimated_complexity,
                    "architecture_summary": summary.architecture_summary,
                },
            )
    except Exception as e:
        print(f"Error in custom rate limit handler: {e}")

    return JSONResponse(
        status_code=200,
        content={
            "result": "AI reasoning is currently unavailable due to rate limits.",
            "status": "fallback",
            "message": "AI reasoning unavailable.",
            "deterministic_analysis_available": False,
        },
    )


@app.on_event("startup")
def startup_event():
    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY missing.", file=sys.stderr)
        print("Please configure your .env file.", file=sys.stderr)
        sys.exit(1)


class ParseRequest(BaseModel):
    directory_path: str
    api_key: Optional[str] = None


class AIReviewResponse(BaseModel):
    result: str
    status: str = "success"
    message: Optional[str] = None
    deterministic_analysis_available: bool = True

    # Optional fields from InfraSummary for fallback
    services: Optional[List[str]] = None
    resources: Optional[List[Resource]] = None
    dependencies: Optional[List[Dependency]] = None
    security_risks: Optional[List[SecurityRisk]] = None
    metrics: Optional[ComplexityMetrics] = None
    estimated_complexity: Optional[str] = None
    architecture_summary: Optional[str] = None


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
    if not os.path.exists(request.directory_path) or not os.path.isdir(
        request.directory_path
    ):
        raise HTTPException(status_code=400, detail="Invalid directory path")

    try:
        builder = ContextBuilder(request.directory_path)
        summary = builder.build_context()
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error parsing infrastructure: {str(e)}"
        )


@app.post("/api/v1/diagram", response_model=DiagramResponse)
def generate_diagram(request: ParseRequest):
    if not os.path.exists(request.directory_path) or not os.path.isdir(
        request.directory_path
    ):
        raise HTTPException(status_code=400, detail="Invalid directory path")

    try:
        builder = ContextBuilder(request.directory_path)
        summary = builder.build_context()
        generator = MermaidGenerator(summary.resources, summary.dependencies)
        mermaid_code = generator.generate()
        return DiagramResponse(mermaid=mermaid_code)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating diagram: {str(e)}"
        )


@app.post("/api/v1/explain", response_model=AIReviewResponse)
@limiter.limit("20/minute")
async def explain_infrastructure(request: Request, parse_request: ParseRequest):
    if not os.path.exists(parse_request.directory_path) or not os.path.isdir(
        parse_request.directory_path
    ):
        raise HTTPException(status_code=400, detail="Invalid directory path")

    try:
        builder = ContextBuilder(parse_request.directory_path)
        summary = builder.build_context()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error parsing infrastructure: {str(e)}"
        )

    try:
        orchestrator = AIOrchestrator(api_key=parse_request.api_key)
        # Timeout at 30 seconds
        result = await asyncio.wait_for(
            asyncio.to_thread(orchestrator.explain_infrastructure, summary),
            timeout=30.0,
        )
        return AIReviewResponse(
            result=result, status="success", deterministic_analysis_available=True
        )
    except asyncio.TimeoutError:
        return AIReviewResponse(
            result="AI request timed out.",
            status="fallback",
            message="AI request timed out.",
            deterministic_analysis_available=True,
            services=summary.services,
            resources=summary.resources,
            dependencies=summary.dependencies,
            security_risks=summary.security_risks,
            metrics=summary.metrics,
            estimated_complexity=summary.estimated_complexity,
            architecture_summary=summary.architecture_summary,
        )
    except Exception as e:
        return AIReviewResponse(
            result=f"AI reasoning unavailable: {str(e)}",
            status="fallback",
            message="AI reasoning unavailable.",
            deterministic_analysis_available=True,
            services=summary.services,
            resources=summary.resources,
            dependencies=summary.dependencies,
            security_risks=summary.security_risks,
            metrics=summary.metrics,
            estimated_complexity=summary.estimated_complexity,
            architecture_summary=summary.architecture_summary,
        )


@app.post("/api/v1/security-review", response_model=AIReviewResponse)
@limiter.limit("20/minute")
async def security_review(request: Request, parse_request: ParseRequest):
    if not os.path.exists(parse_request.directory_path) or not os.path.isdir(
        parse_request.directory_path
    ):
        raise HTTPException(status_code=400, detail="Invalid directory path")

    try:
        builder = ContextBuilder(parse_request.directory_path)
        summary = builder.build_context()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error parsing infrastructure: {str(e)}"
        )

    try:
        orchestrator = AIOrchestrator(api_key=parse_request.api_key)
        # Timeout at 30 seconds
        result = await asyncio.wait_for(
            asyncio.to_thread(orchestrator.review_security, summary),
            timeout=30.0,
        )
        return AIReviewResponse(
            result=result, status="success", deterministic_analysis_available=True
        )
    except asyncio.TimeoutError:
        return AIReviewResponse(
            result="AI request timed out.",
            status="fallback",
            message="AI request timed out.",
            deterministic_analysis_available=True,
            services=summary.services,
            resources=summary.resources,
            dependencies=summary.dependencies,
            security_risks=summary.security_risks,
            metrics=summary.metrics,
            estimated_complexity=summary.estimated_complexity,
            architecture_summary=summary.architecture_summary,
        )
    except Exception as e:
        return AIReviewResponse(
            result=f"AI reasoning unavailable: {str(e)}",
            status="fallback",
            message="AI reasoning unavailable.",
            deterministic_analysis_available=True,
            services=summary.services,
            resources=summary.resources,
            dependencies=summary.dependencies,
            security_risks=summary.security_risks,
            metrics=summary.metrics,
            estimated_complexity=summary.estimated_complexity,
            architecture_summary=summary.architecture_summary,
        )


@app.post("/api/v1/cost-review", response_model=AIReviewResponse)
@limiter.limit("20/minute")
async def cost_review(request: Request, parse_request: ParseRequest):
    if not os.path.exists(parse_request.directory_path) or not os.path.isdir(
        parse_request.directory_path
    ):
        raise HTTPException(status_code=400, detail="Invalid directory path")

    try:
        builder = ContextBuilder(parse_request.directory_path)
        summary = builder.build_context()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error parsing infrastructure: {str(e)}"
        )

    try:
        orchestrator = AIOrchestrator(api_key=parse_request.api_key)
        # Timeout at 30 seconds
        result = await asyncio.wait_for(
            asyncio.to_thread(orchestrator.review_cost, summary),
            timeout=30.0,
        )
        return AIReviewResponse(
            result=result, status="success", deterministic_analysis_available=True
        )
    except asyncio.TimeoutError:
        return AIReviewResponse(
            result="AI request timed out.",
            status="fallback",
            message="AI request timed out.",
            deterministic_analysis_available=True,
            services=summary.services,
            resources=summary.resources,
            dependencies=summary.dependencies,
            security_risks=summary.security_risks,
            metrics=summary.metrics,
            estimated_complexity=summary.estimated_complexity,
            architecture_summary=summary.architecture_summary,
        )
    except Exception as e:
        return AIReviewResponse(
            result=f"AI reasoning unavailable: {str(e)}",
            status="fallback",
            message="AI reasoning unavailable.",
            deterministic_analysis_available=True,
            services=summary.services,
            resources=summary.resources,
            dependencies=summary.dependencies,
            security_risks=summary.security_risks,
            metrics=summary.metrics,
            estimated_complexity=summary.estimated_complexity,
            architecture_summary=summary.architecture_summary,
        )
