from typing import List

from app.schemas.infra_schema import Resource, SecurityRisk


class DockerSecurityAnalyzer:
    def __init__(self, resources: List[Resource]):
        self.resources = resources

    def analyze(self) -> List[SecurityRisk]:
        risks = []
        risks.extend(self._check_dockerfiles())
        risks.extend(self._check_compose_services())
        return risks

    def _check_dockerfiles(self) -> List[SecurityRisk]:
        risks = []
        for res in self.resources:
            if res.service_name == "DOCKER_IMAGE":
                attributes = res.attributes
                base_image = attributes.get("base_image", "")
                users = attributes.get("users", [])

                if ":latest" in base_image or (
                    ":" not in base_image and base_image != "unknown"
                ):
                    risks.append(
                        SecurityRisk(
                            severity="MEDIUM",
                            category="containers",
                            description=f"Dockerfile uses 'latest' image tag: {base_image}",
                            recommendation="Pin base images to specific versions or SHAs.",
                            resource_id=f"{res.resource_type}.{res.name}",
                            file_path=res.file_path,
                            line_number=res.line_start,
                        )
                    )

                # If no USER is specified or the last USER is root
                if not users or users[-1] == "root" or users[-1] == "0":
                    risks.append(
                        SecurityRisk(
                            severity="HIGH",
                            category="permissions",
                            description="Dockerfile executes as root user",
                            recommendation="Add 'USER nonroot' to run the container as a non-privileged user.",
                            resource_id=f"{res.resource_type}.{res.name}",
                            file_path=res.file_path,
                            line_number=res.line_start,
                        )
                    )

                if "22" in attributes.get("exposed_ports", []):
                    risks.append(
                        SecurityRisk(
                            severity="HIGH",
                            category="networking",
                            description="Dockerfile exposes port 22 (SSH)",
                            recommendation="Remove SSH from containers. Use docker exec for debugging.",
                            resource_id=f"{res.resource_type}.{res.name}",
                            file_path=res.file_path,
                            line_number=res.line_start,
                        )
                    )
        return risks

    def _check_compose_services(self) -> List[SecurityRisk]:
        risks = []
        for res in self.resources:
            if res.service_name == "COMPOSE_SERVICE":
                attributes = res.attributes

                if attributes.get("privileged", False):
                    risks.append(
                        SecurityRisk(
                            severity="CRITICAL",
                            category="permissions",
                            description="Compose service runs as privileged",
                            recommendation="Remove privileged flag and grant specific capabilities.",
                            resource_id=f"{res.resource_type}.{res.name}",
                            file_path=res.file_path,
                            line_number=res.line_start,
                        )
                    )

                if attributes.get("network_mode") == "host":
                    risks.append(
                        SecurityRisk(
                            severity="HIGH",
                            category="networking",
                            description="Compose service uses host networking",
                            recommendation="Use bridged networks to isolate container traffic.",
                            resource_id=f"{res.resource_type}.{res.name}",
                            file_path=res.file_path,
                            line_number=res.line_start,
                        )
                    )

                volumes = attributes.get("volumes", [])
                for vol in volumes:
                    if isinstance(vol, str) and "docker.sock" in vol:
                        risks.append(
                            SecurityRisk(
                                severity="CRITICAL",
                                category="permissions",
                                description="Docker socket mounted in container",
                                recommendation="Avoid mounting the docker socket, as it allows container escape and root access to the host.",
                                resource_id=f"{res.resource_type}.{res.name}",
                                file_path=res.file_path,
                                line_number=res.line_start,
                            )
                        )
        return risks
