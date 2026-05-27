from typing import List

from app.schemas.infra_schema import Dependency, Resource


class DockerDependencySolver:
    def __init__(self, resources: List[Resource]):
        self.resources = resources

    def solve(self) -> List[Dependency]:
        dependencies = []

        for res in self.resources:
            if res.service_name == "COMPOSE_SERVICE":
                attributes = res.attributes
                depends_on = attributes.get("depends_on", [])

                # depends_on can be a list or a dict
                target_services = []
                if isinstance(depends_on, list):
                    target_services = depends_on
                elif isinstance(depends_on, dict):
                    target_services = list(depends_on.keys())

                for target_svc in target_services:
                    for tgt in self.resources:
                        if (
                            tgt.service_name == "COMPOSE_SERVICE"
                            and tgt.name == target_svc
                        ):
                            dependencies.append(
                                Dependency(
                                    source=f"{res.resource_type}.{res.name}",
                                    target=f"{tgt.resource_type}.{tgt.name}",
                                    relationship="depends_on",
                                )
                            )

        return dependencies
