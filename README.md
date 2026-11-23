# AI Agents in CI/CD Pipelines: A Practical Guide to Agentic DevOps

The Spring Boot order service is the main lab. You’ll make a real Maven integration test fail, watch an agent diagnose it and verify one scoped repair, review the evidence, and take the corrected service through GitHub CI/CD.

## Start with the Spring Boot lab

1. [Run the order API](spring-boot-sample/README.md) and verify that orders of $50 or more ship free.
2. [Run the agent exercise](docs/java-agent-lab.md) in observe and repair modes. Inspect the failing test, smoke-test results, JSON audit, and candidate patch.
3. Review the patch on a disposable branch and run **Spring Boot Delivery** through a pull request. Follow the [release guide](docs/github-release.md) to verify and deploy the published artifact.

The smaller Python example remains available through the [lab workbook](docs/labs.md) for practicing the control loop without Maven.

## GitHub development and release

Use the issue form and PR checklist to track a change. Actions verify the Python lab and Java service, run CodeQL on both languages, and stage the verified build. Dependabot checks Maven, container base images, and Actions pins. A version tag on `main` publishes the tested JAR, CycloneDX SBOM, checksums, and a container reference with GitHub attestations.

See [Security and quality controls](docs/security-quality.md) for alert routing, coverage, and administrator settings.

See [GitHub releases and deployment](docs/github-release.md) for release, verification, and rollback commands.

## Hands-on labs and enterprise workflows

- [Lab workbook](docs/labs.md) covers PR checks, artifact promotion, rollback, and repair review.
- [Environment setup and operations](docs/operations.md) covers GitHub rulesets, staging approvals, credentials, and running on a private target.
- [Editable draw.io workflows](docs/workflows.drawio) show CI/CD promotion, repair review, rollback, and Spring Boot delivery. Open the file in diagrams.net or the draw.io desktop app.

## Follow the control loop

| Phase | What happens |
| --- | --- |
| Perceive | Run the Spring Boot HTTP integration suite and identify the failing test in Maven Surefire XML. |
| Reason | Match the exact boundary failure to the runbook. Use the offline rule or ask a configured model to choose between the prescribed repair and escalation. |
| Act | Apply one known replacement in a temporary copy, scoped to the sample shipping function. |
| Verify | Run Maven verification, launch the executable JAR, and smoke-test order creation and retrieval before exporting a patch. |
| Learn | Record the decision, verification result, and CI run ID in a JSON artifact for review across runs. The audit is historical evidence. |

## Runbook and review

**Known issue:** When the sole failure is that the exact threshold returns 599 instead of 0, restore the inclusive comparison. Unexpected failures, model errors, and rejected repairs go to a maintainer. If verification fails, the audit records the result and the run produces no candidate patch.

**Approval:** Compare the patch with the initial and verification logs. The patch applies to a copy containing the injected regression. For a real branch with the same defect, a maintainer can review and apply the equivalent change through a pull request. The lab itself produces the review artifact. Automated pull request creation and production deployment are outside this demo.

## Optional AI decision

Add an Actions repository secret named `AI_GATEWAY_API_KEY` for Vercel AI Gateway, then dispatch the regression scenario on `main`. The model receives a fixed synthetic observation and chooses an allowlisted action. The gate independently checks the failure and the candidate source. Without a key the same workflow uses an offline rule, so reviewers can reproduce the demo without a provider account.

Based on the control-loop and staged rollout described in Vishvesh Patel’s *AI Agents in CI/CD Pipelines: A Practical Guide to Agentic DevOps*.
