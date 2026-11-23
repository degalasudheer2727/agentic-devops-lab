# Agentic DevOps Lab

A Spring Boot order service and an end-to-end DevSecOps pipeline. Reproduce a shipping regression, review an agent-generated repair, and follow the corrected build through testing, security gates, staging, and an attested GitHub release.

## Start here

1. [Run the Spring Boot order API](services/orders/README.md).
2. [Run the agent repair lab](docs/java-agent-lab.md) and review the patch and audit evidence.
3. [Work through CI, security, and rollback exercises](docs/labs.md).
4. [Verify and deploy a GitHub release](docs/github-release.md).

## Repository layout

| Path | Purpose |
| --- | --- |
| `services/orders/` | Java API, integration tests, Dockerfile, and runtime smoke checks |
| `labs/order-agent/` | Bounded repair exercise and optional model decision |
| `tools/ci/` | Scanner installation and container smoke checks |
| `.github/` | Actions, Dependabot, issue form, and PR template |
| `docs/` | Lab workbook, release runbook, security controls, and editable draw.io diagrams |

The delivery pipeline tests the Java service, checks coverage, scans source and workflows, checks dependencies, detects secrets, tests the container configuration, and scans the built image. Staging and GitHub Releases use the same checked image archive. See the [control matrix](docs/security-quality.md), [operations runbook](docs/operations.md), and [draw.io workflows](docs/workflows.drawio).

The demonstration uses a temporary GitHub runner for staging. The [release guide](docs/github-release.md) shows how to verify and run an image by digest in your own environment.
