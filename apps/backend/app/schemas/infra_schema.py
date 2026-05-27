from typing import List, Optional

from pydantic import BaseModel


class Resource(BaseModel):
    resource_type: str
    name: str
    provider: str
    service_name: str
    attributes: dict
    file_path: Optional[str] = None
    line_start: Optional[int] = None


class Dependency(BaseModel):
    source: str
    target: str
    relationship: str


class SecurityRisk(BaseModel):
    severity: str
    category: str
    description: str
    recommendation: str
    resource_id: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None


class ComplexityMetrics(BaseModel):
    total_resources: int
    public_exposure_count: int
    iam_risk_count: int
    network_depth: int


class InfraSummary(BaseModel):
    services: List[str]
    resources: List[Resource]
    dependencies: List[Dependency]
    security_risks: List[SecurityRisk]
    metrics: ComplexityMetrics
    estimated_complexity: str
    architecture_summary: str
