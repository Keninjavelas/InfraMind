from typing import List

from app.schemas.infra_schema import Dependency, Resource


class MermaidGenerator:
    def __init__(self, resources: List[Resource], dependencies: List[Dependency]):
        self.resources = resources
        self.dependencies = dependencies
        self.resource_map = {f"{r.resource_type}.{r.name}": r for r in resources}

    def generate(self) -> str:
        lines = ["graph TD"]
        service_edges = set()

        for dep in self.dependencies:
            source_res = self.resource_map.get(dep.source)
            target_res = self.resource_map.get(dep.target)

            if source_res and target_res:
                source_svc = source_res.service_name
                target_svc = target_res.service_name

                if source_svc != target_svc:
                    # To make traffic flow more logical visually, we can flip certain edges
                    # For example, ECS depends on RDS in terraform, but traffic flows ECS -> RDS. That matches.
                    # ECS depends on TargetGroup, TargetGroup attached to ALB.
                    # For MVP, we'll just plot them exactly as they depend, or reverse common ones.

                    if "ALB" in source_svc and "Target Group" in target_svc:
                        service_edges.add(("ALB", "Target Group"))
                    elif "ECS" in source_svc and "Target Group" in target_svc:
                        service_edges.add(("Target Group", "ECS"))
                    else:
                        service_edges.add((source_svc, target_svc))

        exposed_services = [r.service_name for r in self.resources]
        if "ALB" in exposed_services:
            service_edges.add(("Internet", "ALB"))
        elif "IGW" in exposed_services:
            service_edges.add(("Internet", "IGW"))

        for src, tgt in service_edges:
            lines.append(f"    {src} --> {tgt}")

        if len(service_edges) == 0:
            for r in self.resources:
                lines.append(f"    {r.service_name}")

        # unique lines
        unique_lines = list(dict.fromkeys(lines))
        return "\n".join(unique_lines)
