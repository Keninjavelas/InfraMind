from typing import List

from app.schemas.infra_schema import Resource, SecurityRisk


class KubernetesSecurityAnalyzer:
    def __init__(self, resources: List[Resource]):
        self.resources = resources

    def analyze(self) -> List[SecurityRisk]:
        risks = []
        risks.extend(self._check_pod_security())
        risks.extend(self._check_services_and_ingress())
        risks.extend(self._check_secrets())
        return risks

    def _extract_containers(self, spec: dict) -> List[dict]:
        containers = []
        template_spec = spec.get("template", {}).get("spec", {})
        containers.extend(template_spec.get("containers", []))
        containers.extend(template_spec.get("initContainers", []))
        return containers

    def _check_pod_security(self) -> List[SecurityRisk]:
        risks = []
        for res in self.resources:
            if res.service_name in [
                "K8S_DEPLOYMENT",
                "K8S_STATEFULSET",
                "K8S_DAEMONSET",
            ]:
                spec = res.attributes.get("spec", {})
                containers = self._extract_containers(spec)

                for container in containers:
                    image = container.get("image", "")
                    if ":latest" in image or ":" not in image:
                        risks.append(
                            SecurityRisk(
                                severity="MEDIUM",
                                category="containers",
                                description=f"Container '{container.get('name')}' uses 'latest' image tag",
                                recommendation="Pin container images to specific versions or SHAs.",
                                resource_id=f"{res.resource_type}.{res.name}",
                                file_path=res.file_path,
                                line_number=res.line_start,
                            )
                        )

                    security_context = container.get("securityContext", {})
                    if security_context.get("privileged", False):
                        risks.append(
                            SecurityRisk(
                                severity="CRITICAL",
                                category="permissions",
                                description=f"Container '{container.get('name')}' runs as privileged",
                                recommendation="Remove privileged flag and grant specific capabilities.",
                                resource_id=f"{res.resource_type}.{res.name}",
                                file_path=res.file_path,
                                line_number=res.line_start,
                            )
                        )

                    if (
                        security_context.get("runAsRoot", False)
                        or security_context.get("runAsUser") == 0
                    ):
                        risks.append(
                            SecurityRisk(
                                severity="HIGH",
                                category="permissions",
                                description=f"Container '{container.get('name')}' is explicitly running as root",
                                recommendation="Set runAsNonRoot: true in securityContext.",
                                resource_id=f"{res.resource_type}.{res.name}",
                                file_path=res.file_path,
                                line_number=res.line_start,
                            )
                        )
        return risks

    def _check_services_and_ingress(self) -> List[SecurityRisk]:
        risks = []
        for res in self.resources:
            if res.service_name == "K8S_SERVICE":
                service_type = res.attributes.get("spec", {}).get("type", "ClusterIP")
                if service_type in ["LoadBalancer", "NodePort"]:
                    risks.append(
                        SecurityRisk(
                            severity="MEDIUM",
                            category="networking",
                            description=f"Service exposes ports via {service_type}",
                            recommendation="Ensure this service is intended for public or wide internal exposure.",
                            resource_id=f"{res.resource_type}.{res.name}",
                            file_path=res.file_path,
                            line_number=res.line_start,
                        )
                    )
        return risks

    def _check_secrets(self) -> List[SecurityRisk]:
        risks = []
        for res in self.resources:
            if res.service_name == "K8S_SECRET":
                # K8s secrets are base64 encoded, not encrypted. Storing them in plaintext manifests is a risk.
                risks.append(
                    SecurityRisk(
                        severity="HIGH",
                        category="secrets",
                        description="Secret defined directly in manifest",
                        recommendation="Use external secret management (e.g. AWS Secrets Manager, HashiCorp Vault) or Sealed Secrets.",
                        resource_id=f"{res.resource_type}.{res.name}",
                        file_path=res.file_path,
                        line_number=res.line_start,
                    )
                )
        return risks
