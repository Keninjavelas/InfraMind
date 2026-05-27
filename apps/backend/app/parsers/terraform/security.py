from typing import Any, Dict, List

from app.schemas.infra_schema import Resource, SecurityRisk


class SecurityAnalyzer:
    def __init__(self, resources: List[Resource]):
        self.resources = resources

    def analyze(self) -> List[SecurityRisk]:
        risks = []
        risks.extend(self._check_open_security_groups())
        risks.extend(self._check_public_s3_buckets())
        risks.extend(self._check_wildcard_iam_policies())
        return risks

    def _check_open_security_groups(self) -> List[SecurityRisk]:
        risks = []
        for res in self.resources:
            if (
                res.resource_type == "aws_security_group"
                or res.resource_type == "aws_security_group_rule"
            ):
                ingress = res.attributes.get("ingress", [])
                if isinstance(ingress, list):
                    for rule in ingress:
                        if isinstance(rule, dict) and "cidr_blocks" in rule:
                            cidr = rule.get("cidr_blocks", [])
                            if not isinstance(cidr, list):
                                cidr = [cidr]
                            cidr_cleaned = [
                                c.strip("\"'") if isinstance(c, str) else c
                                for c in cidr
                            ]
                            if "0.0.0.0/0" in cidr_cleaned:
                                risks.append(
                                    SecurityRisk(
                                        severity="CRITICAL",
                                        category="networking",
                                        description="Security Group exposes port to 0.0.0.0/0 (Global)",
                                        recommendation="Restrict CIDR blocks to known IPs or VPC CIDR.",
                                        resource_id=f"{res.resource_type}.{res.name}",
                                        file_path=res.file_path,
                                        line_number=res.line_start,
                                    )
                                )
        return risks

    def _check_public_s3_buckets(self) -> List[SecurityRisk]:
        risks = []
        for res in self.resources:
            if res.resource_type == "aws_s3_bucket":
                acl = res.attributes.get("acl", "")
                if isinstance(acl, str) and acl.strip("\"'") in [
                    "public-read",
                    "public-read-write",
                ]:
                    risks.append(
                        SecurityRisk(
                            severity="HIGH",
                            category="storage",
                            description=f"S3 Bucket has public ACL: {acl}",
                            recommendation="Set ACL to private or rely on bucket policies.",
                            resource_id=f"{res.resource_type}.{res.name}",
                            file_path=res.file_path,
                            line_number=res.line_start,
                        )
                    )
        return risks

    def _check_wildcard_iam_policies(self) -> List[SecurityRisk]:
        risks = []
        for res in self.resources:
            if res.resource_type in ["aws_iam_policy", "aws_iam_role_policy"]:
                policy = str(res.attributes.get("policy", ""))
                policy_no_space = policy.replace(" ", "")
                if (
                    '"Action": "*"' in policy
                    or "'Action': '*'" in policy
                    or '"Action":["*"]' in policy_no_space
                    or 'Action="*"' in policy_no_space
                ):
                    risks.append(
                        SecurityRisk(
                            severity="HIGH",
                            category="iam",
                            description="IAM Policy contains wildcard action '*'",
                            recommendation="Apply principle of least privilege.",
                            resource_id=f"{res.resource_type}.{res.name}",
                            file_path=res.file_path,
                            line_number=res.line_start,
                        )
                    )
        return risks
