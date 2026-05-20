---
name: False Positive Report
about: Report a security or architecture diagnostic that flagged incorrectly
title: "[FALSE POSITIVE] "
labels: false-positive
assignees: ''
---

**Which resource was flagged incorrectly?**
Please provide the type of resource (e.g. `aws_security_group`, `Kubernetes Deployment`, etc).

**Provide the infrastructure code snippet**
```hcl/yaml/dockerfile
# Paste the snippet that caused the false positive here
```

**What diagnostic was generated?**
(e.g., "CRITICAL: Security Group exposes port to 0.0.0.0/0")

**Why is this a false positive?**
Explain why the configuration is actually secure or intentionally designed this way.

**Expected behavior**
InfraMind should not flag this resource, or should downgrade the severity to INFO.
