from typing import List, Dict
from app.schemas.infra_schema import Resource, Dependency

class KubernetesDependencySolver:
    def __init__(self, resources: List[Resource]):
        self.resources = resources
        
    def _find_resources_by_labels(self, target_service_name: str, labels: dict) -> List[Resource]:
        matches = []
        for res in self.resources:
            if res.service_name == target_service_name:
                res_labels = res.attributes.get('labels', {})
                # Check if all selector labels match resource labels
                if all(res_labels.get(k) == v for k, v in labels.items()):
                    matches.append(res)
        return matches

    def solve(self) -> List[Dependency]:
        dependencies = []
        
        # Ingress -> Service
        for res in self.resources:
            if res.service_name == "K8S_INGRESS":
                rules = res.attributes.get('spec', {}).get('rules', [])
                for rule in rules:
                    paths = rule.get('http', {}).get('paths', [])
                    for path in paths:
                        service_name = path.get('backend', {}).get('service', {}).get('name')
                        if service_name:
                            # Look for the service
                            for tgt in self.resources:
                                if tgt.service_name == "K8S_SERVICE" and tgt.name.endswith(f"/{service_name}"):
                                    dependencies.append(Dependency(
                                        source=f"{res.resource_type}.{res.name}",
                                        target=f"{tgt.resource_type}.{tgt.name}",
                                        relationship="routes_to"
                                    ))
                                    break
                                    
        # Service -> Deployment/StatefulSet/DaemonSet
        for res in self.resources:
            if res.service_name == "K8S_SERVICE":
                selector = res.attributes.get('spec', {}).get('selector', {})
                if selector:
                    for target_kind in ["K8S_DEPLOYMENT", "K8S_STATEFULSET", "K8S_DAEMONSET"]:
                        targets = self._find_resources_by_labels(target_kind, selector)
                        for tgt in targets:
                            dependencies.append(Dependency(
                                source=f"{res.resource_type}.{res.name}",
                                target=f"{tgt.resource_type}.{tgt.name}",
                                relationship="selects"
                            ))
                            
        # Workload -> ConfigMap/Secret
        for res in self.resources:
            if res.service_name in ["K8S_DEPLOYMENT", "K8S_STATEFULSET", "K8S_DAEMONSET"]:
                spec = res.attributes.get('spec', {})
                template_spec = spec.get('template', {}).get('spec', {})
                
                # Volumes
                volumes = template_spec.get('volumes', [])
                for vol in volumes:
                    if 'configMap' in vol:
                        cm_name = vol['configMap'].get('name')
                        for tgt in self.resources:
                            if tgt.service_name == "K8S_CONFIGMAP" and tgt.name.endswith(f"/{cm_name}"):
                                dependencies.append(Dependency(
                                    source=f"{res.resource_type}.{res.name}",
                                    target=f"{tgt.resource_type}.{tgt.name}",
                                    relationship="mounts"
                                ))
                    elif 'secret' in vol:
                        secret_name = vol['secret'].get('secretName')
                        for tgt in self.resources:
                            if tgt.service_name == "K8S_SECRET" and tgt.name.endswith(f"/{secret_name}"):
                                dependencies.append(Dependency(
                                    source=f"{res.resource_type}.{res.name}",
                                    target=f"{tgt.resource_type}.{tgt.name}",
                                    relationship="mounts"
                                ))
                                
                # EnvFrom
                containers = template_spec.get('containers', [])
                for container in containers:
                    env_from = container.get('envFrom', [])
                    for env in env_from:
                        if 'configMapRef' in env:
                            cm_name = env['configMapRef'].get('name')
                            for tgt in self.resources:
                                if tgt.service_name == "K8S_CONFIGMAP" and tgt.name.endswith(f"/{cm_name}"):
                                    dependencies.append(Dependency(
                                        source=f"{res.resource_type}.{res.name}",
                                        target=f"{tgt.resource_type}.{tgt.name}",
                                        relationship="env_from"
                                    ))
                        elif 'secretRef' in env:
                            secret_name = env['secretRef'].get('name')
                            for tgt in self.resources:
                                if tgt.service_name == "K8S_SECRET" and tgt.name.endswith(f"/{secret_name}"):
                                    dependencies.append(Dependency(
                                        source=f"{res.resource_type}.{res.name}",
                                        target=f"{tgt.resource_type}.{tgt.name}",
                                        relationship="env_from"
                                    ))
                                
        return dependencies
