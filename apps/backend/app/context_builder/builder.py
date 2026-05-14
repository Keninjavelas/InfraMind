from typing import Dict, Any
from app.schemas.infra_schema import InfraSummary, ComplexityMetrics
from app.parsers.terraform.parser import TerraformParser
from app.parsers.terraform.resources import ResourceExtractor
from app.parsers.terraform.security import SecurityAnalyzer
from app.parsers.terraform.dependencies import DependencyResolver

class ContextBuilder:
    def __init__(self, directory: str):
        self.directory = directory
        
    def build_context(self) -> InfraSummary:
        # 1. Parse Terraform
        parser = TerraformParser(self.directory)
        parsed_data = parser.load_files()
        
        # 2. Extract Resources & Services
        extractor = ResourceExtractor(parsed_data)
        resources = extractor.extract_resources()
        services = extractor.extract_services()
        
        # 3. Resolve Dependencies
        resolver = DependencyResolver(resources)
        dependencies = resolver.resolve()
        
        # 4. Analyze Security
        analyzer = SecurityAnalyzer(resources)
        risks = analyzer.analyze()
        
        # 5. Compute Complexity Metrics
        public_exposure_count = len([r for r in risks if r.category == "networking" and r.severity == "CRITICAL"])
        iam_risk_count = len([r for r in risks if r.category == "iam"])
        # A simple proxy for network depth: number of dependencies related to networking (can be refined)
        network_depth = len(dependencies) 
        
        metrics = ComplexityMetrics(
            total_resources=len(resources),
            public_exposure_count=public_exposure_count,
            iam_risk_count=iam_risk_count,
            network_depth=network_depth
        )
        
        # 6. Synthesize Summary
        complexity = "LOW"
        if metrics.total_resources > 20 or metrics.public_exposure_count > 2:
            complexity = "HIGH"
        elif metrics.total_resources > 5 or network_depth > 5:
            complexity = "MEDIUM"
            
        arch_summary = "Basic infrastructure components."
        if "EC2" in services and "RDS" in services:
             arch_summary = "Application hosted on EC2 with RDS database."
        elif "ECS" in services:
             arch_summary = "Containerized architecture on ECS."
             
        return InfraSummary(
            services=services,
            resources=resources,
            dependencies=dependencies,
            security_risks=risks,
            metrics=metrics,
            estimated_complexity=complexity,
            architecture_summary=arch_summary
        )
