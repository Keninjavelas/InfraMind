import re
from typing import Dict, Any, List
from app.schemas.infra_schema import Resource

class KubernetesResourceExtractor:
    def __init__(self, manifests: List[Dict[str, Any]]):
        self.manifests = manifests
        self.supported_kinds = [
            "Deployment", "Service", "Ingress", "ConfigMap", 
            "Secret", "StatefulSet", "DaemonSet"
        ]

    def _normalize_service_name(self, kind: str) -> str:
        return f"K8S_{kind.upper()}"

    def _find_line_number(self, content: str, name: str) -> int:
        pattern = re.compile(rf'name:\s+["\']?{name}["\']?')
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if pattern.search(line):
                return i + 1
        return 1

    def extract_resources(self) -> List[Resource]:
        resources = []
        
        for manifest in self.manifests:
            kind = manifest.get('kind')
            if kind not in self.supported_kinds:
                continue
                
            metadata = manifest.get('metadata', {})
            name = metadata.get('name', 'unknown')
            namespace = metadata.get('namespace', 'default')
            
            file_path = manifest.pop('__file_path', None)
            content = manifest.pop('__content', "")
            line_start = self._find_line_number(content, name) if file_path else None
            
            # Combine relevant info into attributes
            attributes = {
                "namespace": namespace,
                "labels": metadata.get('labels', {}),
                "annotations": metadata.get('annotations', {}),
                "spec": manifest.get('spec', {}),
                "data": manifest.get('data', {}), # For ConfigMap/Secret
            }
            
            resources.append(Resource(
                resource_type=f"kubernetes_{kind.lower()}",
                name=f"{namespace}/{name}",
                provider="kubernetes",
                service_name=self._normalize_service_name(kind),
                attributes=attributes,
                file_path=file_path,
                line_start=line_start
            ))
            
        return resources
