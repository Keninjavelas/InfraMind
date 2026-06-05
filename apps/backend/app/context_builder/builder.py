from typing import Any, Dict, List

from app.parsers.docker.dependencies import DockerDependencySolver
from app.parsers.docker.parser import DockerParser
from app.parsers.docker.resources import DockerResourceExtractor
from app.parsers.docker.security import DockerSecurityAnalyzer
from app.parsers.kubernetes.dependencies import KubernetesDependencySolver
from app.parsers.kubernetes.parser import KubernetesParser
from app.parsers.kubernetes.resources import KubernetesResourceExtractor
from app.parsers.kubernetes.security import KubernetesSecurityAnalyzer
from app.parsers.terraform.dependencies import \
    DependencyResolver as TFDependencyResolver
from app.parsers.terraform.parser import TerraformParser
from app.parsers.terraform.resources import \
    ResourceExtractor as TFResourceExtractor
from app.parsers.terraform.security import \
    SecurityAnalyzer as TFSecurityAnalyzer
from app.schemas.infra_schema import (ComplexityMetrics, Dependency,
                                      InfraSummary, Resource, SecurityRisk)


class ContextBuilder:
    def __init__(self, directory: str):
        self.directory = directory

    def build_context(self) -> InfraSummary:
        all_resources: List[Resource] = []
        all_dependencies: List[Dependency] = []
        all_risks: List[SecurityRisk] = []
        all_services = set()

        # 1. Parse Terraform
        try:
            tf_parser = TerraformParser(self.directory)
            tf_data = tf_parser.load_files()
            tf_extractor = TFResourceExtractor(tf_data)
            tf_resources = tf_extractor.extract_resources()

            all_resources.extend(tf_resources)
            for s in tf_extractor.extract_services():
                all_services.add(s)

            tf_resolver = TFDependencyResolver(tf_resources)
            all_dependencies.extend(tf_resolver.resolve())

            tf_analyzer = TFSecurityAnalyzer(tf_resources)
            all_risks.extend(tf_analyzer.analyze())
        except Exception as e:
            print(f"Terraform parsing failed: {e}")

        # 2. Parse Kubernetes
        try:
            k8s_parser = KubernetesParser(self.directory)
            k8s_data = k8s_parser.load_files()
            k8s_extractor = KubernetesResourceExtractor(k8s_data)
            k8s_resources = k8s_extractor.extract_resources()

            all_resources.extend(k8s_resources)
            for res in k8s_resources:
                all_services.add(res.service_name)

            k8s_resolver = KubernetesDependencySolver(k8s_resources)
            all_dependencies.extend(k8s_resolver.solve())

            k8s_analyzer = KubernetesSecurityAnalyzer(k8s_resources)
            all_risks.extend(k8s_analyzer.analyze())
        except Exception as e:
            print(f"Kubernetes parsing failed: {e}")

        # 3. Parse Docker
        try:
            docker_parser = DockerParser(self.directory)
            docker_data = docker_parser.load_files()
            docker_extractor = DockerResourceExtractor(docker_data)
            docker_resources = docker_extractor.extract_resources()

            all_resources.extend(docker_resources)
            for res in docker_resources:
                all_services.add(res.service_name)

            docker_resolver = DockerDependencySolver(docker_resources)
            all_dependencies.extend(docker_resolver.solve())

            docker_analyzer = DockerSecurityAnalyzer(docker_resources)
            all_risks.extend(docker_analyzer.analyze())
        except Exception as e:
            print(f"Docker parsing failed: {e}")

        # Compute Complexity Metrics
        public_exposure_count = len(
            [
                r
                for r in all_risks
                if r.category in ["networking", "permissions"]
                and r.severity == "CRITICAL"
            ]
        )
        iam_risk_count = len([r for r in all_risks if r.category in ["iam", "secrets"]])
        network_depth = len(all_dependencies)

        metrics = ComplexityMetrics(
            total_resources=len(all_resources),
            public_exposure_count=public_exposure_count,
            iam_risk_count=iam_risk_count,
            network_depth=network_depth,
        )

        # Synthesize Summary
        complexity = "LOW"
        if metrics.total_resources > 20 or metrics.public_exposure_count > 2:
            complexity = "HIGH"
        elif metrics.total_resources > 5 or network_depth > 5:
            complexity = "MEDIUM"

        arch_summary = "Basic infrastructure components."
        if "EC2" in all_services and "RDS" in all_services:
            arch_summary = "Application hosted on EC2 with RDS database."
        elif (
            "ECS" in all_services
            or "K8S_DEPLOYMENT" in all_services
            or "COMPOSE_SERVICE" in all_services
        ):
            arch_summary = "Containerized architecture."

        return InfraSummary(
            services=list(all_services),
            resources=all_resources,
            dependencies=all_dependencies,
            security_risks=all_risks,
            metrics=metrics,
            estimated_complexity=complexity,
            architecture_summary=arch_summary,
        )
