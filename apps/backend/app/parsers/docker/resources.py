import os
from typing import Any, Dict, List

from app.schemas.infra_schema import Resource


class DockerResourceExtractor:
    def __init__(self, docker_data: Dict[str, List[Any]]):
        self.docker_data = docker_data

    def _find_line_number(self, content: str, search_str: str) -> int:
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if search_str in line:
                return i + 1
        return 1

    def extract_resources(self) -> List[Resource]:
        resources = []

        # 1. Parse Dockerfiles
        for df in self.docker_data.get("dockerfiles", []):
            content = df.get("__content", "")
            file_path = df.get("__file_path", "")

            # Simple line parsing
            lines = content.split("\n")
            base_image = "unknown"
            exposed_ports = []
            users = []

            for i, line in enumerate(lines):
                line = line.strip()
                if line.startswith("FROM "):
                    base_image = line.split(" ")[1]
                elif line.startswith("EXPOSE "):
                    exposed_ports.append(line.split(" ")[1])
                elif line.startswith("USER "):
                    users.append(line.split(" ")[1])

            attributes = {
                "base_image": base_image,
                "exposed_ports": exposed_ports,
                "users": users,
                "raw_content": content,
            }

            resources.append(
                Resource(
                    resource_type="docker_image",
                    name=f"Dockerfile:{os.path.basename(file_path)}",
                    provider="docker",
                    service_name="DOCKER_IMAGE",
                    attributes=attributes,
                    file_path=file_path,
                    line_start=1,
                )
            )

        # 2. Parse Compose Files
        for compose in self.docker_data.get("compose_files", []):
            content = compose.pop("__content", "")
            file_path = compose.pop("__file_path", "")

            services = compose.get("services", {})
            for svc_name, svc_details in services.items():
                if not isinstance(svc_details, dict):
                    continue

                line_start = self._find_line_number(content, f"{svc_name}:")

                resources.append(
                    Resource(
                        resource_type="docker_compose_service",
                        name=svc_name,
                        provider="docker",
                        service_name="COMPOSE_SERVICE",
                        attributes=svc_details,
                        file_path=file_path,
                        line_start=line_start,
                    )
                )

        return resources
