import os
from typing import Any, Dict, List

import yaml


class DockerParser:
    def __init__(self, directory: str):
        self.directory = directory

    def load_files(self) -> Dict[str, List[Any]]:
        """Reads Dockerfiles and docker-compose.yml files."""
        docker_data = {"dockerfiles": [], "compose_files": []}
        for root, _, files in os.walk(self.directory):
            for file in files:
                file_path = os.path.join(root, file)

                if file == "Dockerfile" or file.endswith(".Dockerfile"):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            docker_data["dockerfiles"].append(
                                {"__file_path": file_path, "__content": content}
                            )
                    except Exception as e:
                        print(f"Error parsing Dockerfile {file_path}: {e}")

                elif file in [
                    "docker-compose.yml",
                    "docker-compose.yaml",
                    "compose.yaml",
                    "compose.yml",
                ]:
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            f.seek(0)
                            compose_dict = yaml.safe_load(f)
                            if isinstance(compose_dict, dict):
                                compose_dict["__file_path"] = file_path
                                compose_dict["__content"] = content
                                docker_data["compose_files"].append(compose_dict)
                    except Exception as e:
                        print(f"Error parsing Docker Compose {file_path}: {e}")

        return docker_data
