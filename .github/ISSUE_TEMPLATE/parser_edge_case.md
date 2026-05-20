---
name: Parser Edge Case
about: Report a failure in parsing valid Terraform, K8s, or Docker syntax
title: "[PARSER] "
labels: edge-case, parser
assignees: ''
---

**Which Parser is failing?**
- [ ] Terraform (HCL)
- [ ] Kubernetes (YAML)
- [ ] Docker (Dockerfile / Compose)

**Provide the infrastructure code snippet**
```hcl/yaml/dockerfile
# Paste the snippet that breaks the parser here
```

**Expected behavior**
How should the parser interpret this block? What dependencies or configurations are being missed or crashing?

**Error Logs (if any)**
Paste any backend exceptions or VS Code extension errors.
