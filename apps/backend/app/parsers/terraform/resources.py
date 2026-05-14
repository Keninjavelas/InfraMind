import re
from typing import Dict, Any, List
from app.schemas.infra_schema import Resource

class ResourceExtractor:
    def __init__(self, parsed_data: Dict[str, Any]):
        self.parsed_data = parsed_data
        
    def _normalize_service_name(self, resource_type: str) -> str:
        service_map = {
            "aws_instance": "EC2",
            "aws_eip": "EC2",
            "aws_ami": "EC2",
            "aws_s3_bucket": "S3",
            "aws_s3_bucket_policy": "S3",
            "aws_ecs_cluster": "ECS",
            "aws_ecs_service": "ECS",
            "aws_ecs_task_definition": "ECS",
            "aws_db_instance": "RDS",
            "aws_iam_role": "IAM",
            "aws_iam_policy": "IAM",
            "aws_iam_role_policy": "IAM",
            "aws_iam_role_policy_attachment": "IAM",
            "aws_security_group": "Security Group",
            "aws_security_group_rule": "Security Group",
            "aws_vpc": "VPC",
            "aws_subnet": "Subnet",
            "aws_internet_gateway": "IGW",
            "aws_route_table": "Route Table",
            "aws_lb": "ALB",
            "aws_alb": "ALB",
            "aws_lb_target_group": "Target Group",
            "aws_lb_listener": "Listener"
        }
        
        if resource_type in service_map:
            return service_map[resource_type]
            
        parts = resource_type.split('_')
        if len(parts) > 1:
            return parts[1].upper()
        return resource_type.upper()

    def _find_line_number(self, content: str, resource_type: str, resource_name: str) -> int:
        pattern = re.compile(rf'resource\s+"{resource_type}"\s+"{resource_name}"')
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if pattern.search(line):
                return i + 1
        return 1

    def extract_resources(self) -> List[Resource]:
        resources = []
        raw_resources = self.parsed_data.get('resource', [])
        
        for res_dict in raw_resources:
            file_path = res_dict.pop('__file_path', None)
            content = res_dict.pop('__content', "")
            
            for res_type, res_instances in res_dict.items():
                for res_name, res_attributes in res_instances.items():
                    provider = res_type.split('_')[0] if '_' in res_type else "unknown"
                    service_name = self._normalize_service_name(res_type)
                    line_start = self._find_line_number(content, res_type, res_name) if file_path else None
                    
                    resources.append(Resource(
                        resource_type=res_type,
                        name=res_name,
                        provider=provider,
                        service_name=service_name,
                        attributes=res_attributes,
                        file_path=file_path,
                        line_start=line_start
                    ))
                    
        return resources
        
    def extract_services(self) -> List[str]:
        resources = self.extract_resources()
        services = set([r.service_name for r in resources])
        return list(services)
