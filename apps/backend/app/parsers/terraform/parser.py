import hcl2
import os
from typing import Dict, Any

class TerraformParser:
    def __init__(self, directory: str):
        self.directory = directory
        
    def load_files(self) -> Dict[str, Any]:
        """Reads all .tf files recursively and parses them into a single Python dictionary."""
        parsed_data = {"resource": [], "data": [], "module": [], "variable": [], "output": []}
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith('.tf'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            f.seek(0)
                            data = hcl2.load(f)
                            # Merge data and attach metadata
                            for key in parsed_data.keys():
                                if key in data:
                                    for item in data[key]:
                                        if isinstance(item, dict):
                                            item['__file_path'] = file_path
                                            item['__content'] = content
                                    parsed_data[key].extend(data[key])
                    except Exception as e:
                        print(f"Error parsing {file_path}: {e}")
        return parsed_data
