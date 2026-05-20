import os
import yaml
from typing import Dict, Any, List

class KubernetesParser:
    def __init__(self, directory: str):
        self.directory = directory
        
    def load_files(self) -> List[Dict[str, Any]]:
        """Reads all .yaml and .yml files recursively and parses them as Kubernetes manifests."""
        manifests = []
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith('.yaml') or file.endswith('.yml'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            f.seek(0)
                            
                            # Support multi-document yaml files
                            docs = yaml.safe_load_all(f)
                            for doc in docs:
                                if isinstance(doc, dict) and 'apiVersion' in doc and 'kind' in doc:
                                    doc['__file_path'] = file_path
                                    doc['__content'] = content
                                    manifests.append(doc)
                    except Exception as e:
                        print(f"Error parsing K8s manifest {file_path}: {e}")
        return manifests
