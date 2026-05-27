import re
from typing import Any, Dict, List

from app.schemas.infra_schema import Dependency, Resource


class DependencyResolver:
    def __init__(self, resources: List[Resource]):
        self.resources = resources
        self.resource_names = {f"{r.resource_type}.{r.name}" for r in resources}

    def resolve(self) -> List[Dependency]:
        dependencies = []

        # Simple regex to catch standard terraform references: type.name.attribute
        # Also catch variables/data etc., but focus on resources for now
        # format: aws_vpc.main.id or ${aws_vpc.main.id}
        ref_pattern = re.compile(
            r"([a-zA-Z0-9_-]+)\.([a-zA-Z0-9_-]+)(?:\.[a-zA-Z0-9_-]+)*"
        )

        def extract_refs(source_id: str, obj: Any):
            if isinstance(obj, str):
                matches = ref_pattern.findall(obj)
                for match in matches:
                    potential_target = f"{match[0]}.{match[1]}"
                    if (
                        potential_target in self.resource_names
                        and potential_target != source_id
                    ):
                        dependencies.append(
                            Dependency(
                                source=source_id,
                                target=potential_target,
                                relationship="references",
                            )
                        )
            elif isinstance(obj, dict):
                for k, v in obj.items():
                    extract_refs(source_id, v)
            elif isinstance(obj, list):
                for item in obj:
                    extract_refs(source_id, item)

        for res in self.resources:
            source_id = f"{res.resource_type}.{res.name}"
            extract_refs(source_id, res.attributes)

        # Deduplicate
        unique_deps = []
        seen = set()
        for d in dependencies:
            sig = (d.source, d.target, d.relationship)
            if sig not in seen:
                seen.add(sig)
                unique_deps.append(d)

        return unique_deps
