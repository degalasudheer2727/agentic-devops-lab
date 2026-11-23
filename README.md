# AI Agents in CI/CD Pipelines: A Practical Guide to Agentic DevOps

A hands-on GitHub Actions lab that demonstrates failure detection, diagnosis, a scoped repair, verification, and human review. The sample storefront offers free shipping at $50. The regression demo changes the comparison from inclusive to exclusive in a temporary copy, so customers at exactly $50 would be charged $5.99.

## Run the lab

Requires Python 3.12 or newer, with no dependencies.

```sh
python -m unittest -v
python lab.py healthy --output lab-results/healthy
python lab.py regression --output lab-results/regression
```

The regression command deliberately exits 1 to preserve the original CI verdict. Open the output directory to inspect the initial failure, verification log, candidate patch, and JSON audit. Use a fresh output directory for each run.

On GitHub, open **Actions → Agentic DevOps Lab → Run workflow**, select `main`, and choose `regression`. Download **lab-evidence** from the run. The manual workflow uses a read-only repository token. The separate **Delivery** workflow validates pull requests and promotes artifacts from `main` to a staging sandbox.

## Java Spring Boot sample

The [Spring Boot order service](spring-boot-sample/README.md) demonstrates request validation, shipping calculation, and database-backed order retrieval. Its GitHub Actions workflow runs Maven integration tests, smoke-tests the executable JAR, and promotes the same verified artifact to the staging sandbox.

## GitHub development and release

Use the issue form and PR checklist to track a change. Actions verify the Python lab and Java service, run CodeQL on both languages, and stage the verified build. Dependabot checks Maven, container base images, and Actions pins. A version tag on `main` publishes the tested JAR, CycloneDX SBOM, checksums, and a container reference with GitHub attestations.

See [GitHub releases and deployment](docs/github-release.md) for release, verification, and rollback commands.

## Hands-on labs and enterprise workflows

- [Lab workbook](docs/labs.md) covers PR checks, artifact promotion, rollback, and repair review.
- [Environment setup and operations](docs/operations.md) covers GitHub rulesets, staging approvals, credentials, and running on a private target.
- [Editable draw.io workflows](docs/workflows.drawio) show CI/CD promotion, repair review, rollback, and Spring Boot delivery. Open the file in diagrams.net or the draw.io desktop app.

## Follow the control loop

| Phase | What happens |
| --- | --- |
| Perceive | Compile the sample and run the shipping tests. Record exit codes and the names of failing checks. |
| Reason | Match the exact boundary failure to the runbook. Use the offline rule or ask a configured model to choose between the prescribed repair and escalation. |
| Act | Apply one known replacement in a temporary copy, scoped to the sample shipping function. |
| Verify | Recompile and rerun the complete suite. Export a patch only after both checks pass. |
| Learn | Record the decision, verification result, and CI run ID in a JSON artifact for review across runs. The audit is historical evidence. |

## Runbook and review

**Known issue:** When the sole failure is that the exact threshold returns 599 instead of 0, restore the inclusive comparison. Unexpected failures, model errors, and rejected repairs go to a maintainer. If verification fails, the audit records the result and the run produces no candidate patch.

**Approval:** Compare the patch with the initial and verification logs. The patch applies to a copy containing the injected regression. For a real branch with the same defect, a maintainer can review and apply the equivalent change through a pull request. The lab itself produces the review artifact. Automated pull request creation and production deployment are outside this demo.

## Optional AI decision

Add an Actions repository secret named `AI_GATEWAY_API_KEY` for Vercel AI Gateway, then dispatch the regression scenario on `main`. The model receives a fixed synthetic observation and chooses an allowlisted action. The gate independently checks the failure and the candidate source. Without a key the same workflow uses an offline rule, so reviewers can reproduce the demo without a provider account.

Based on the control-loop and staged rollout described in Vishvesh Patel’s *AI Agents in CI/CD Pipelines: A Practical Guide to Agentic DevOps*.
