# Spring Boot Agentic DevOps lab

The order API offers free shipping at $50. Changing one comparison from `>=` to `>` makes a $50 order cost an extra $5.99. This exercise traces that regression through a failing HTTP integration test, diagnosis, a verified repair, and human review.

## 1. Run the baseline

From the repository root, use JDK 21, Maven 3.9+, and Python 3.12+.

```bash
mvn -B -ntp -f services/orders/pom.xml clean verify
python3 labs/order-agent/run.py healthy --output lab-results/java-healthy
```

Expect four passing HTTP integration cases and a `healthy` audit result. Use a fresh output directory for each command below.

## 2. Observe, then authorize one repair

```bash
python3 labs/order-agent/run.py regression --mode observe --output lab-results/java-observe
python3 labs/order-agent/run.py regression --mode repair --output lab-results/java-repair
```

Both regression commands intentionally exit with status 1 to preserve the simulated CI failure. Run them separately if your shell exits on errors.

| Evidence | What to check |
| --- | --- |
| `initial.log` | Maven reports a failure in `offersFreeShippingAtThreshold`. The HTTP response charges 599 cents instead of 0. |
| `audit.json` | Observe mode records `diagnosed` with zero attempts. Repair mode records the policy decision, one attempt, and `verified_pending_review` if both verification stages pass. |
| `verification.log` and `smoke.log` | Maven reruns all integration tests and packages the service. The packaged JAR then passes health, order creation, H2 retrieval, and validation checks. |
| `candidate.patch` | The proposed change restores the inclusive comparison in `StoreOrder.java`. |

The agent reads Surefire XML and only accepts the runbook match when the threshold case is the sole failure and the temporary source matches the injected fixture. Unknown failures, model errors, and failed verification escalate. The agent runs a fixed set of tools with time limits and leaves review evidence instead of writing GitHub refs. The deterministic policy works offline. When the optional `AI_GATEWAY_API_KEY` is configured, the repair step sends only a fixed synthetic observation to the model.

## 3. Review the patch in GitHub

Open **Actions → Spring Boot Agent Lab → Run workflow**, choose `main`, and run `regression` in each mode. Download the evidence artifact from the red run. The run is deliberately red when it reproduces the failure. Use the audit outcome to verify what the agent did.

For a PR exercise in a sandbox repository, create a branch and deliberately make the same comparison exclusive in `StoreOrder.java`. Open a PR and verify that **Verify Spring Boot service** fails. Apply the downloaded patch to that branch:

```bash
git apply --check /path/to/candidate.patch
git apply /path/to/candidate.patch
mvn -B -ntp -f services/orders/pom.xml clean verify
```

Commit and push the fix, review the passing checks, and merge through the repository's normal approval process. The main-branch workflow promotes the verified container to the staging sandbox. A separate version tag starts the [release workflow](github-release.md) for GitHub Releases and GHCR.

## 4. Exercise escalation

In a disposable copy, change the below-threshold expected fee in `OrdersApiTest.java` from 599 to 0. Rerun the regression in repair mode. Two cases should fail, the audit should show `escalate`, and the output should contain no candidate patch. Revert the test change after the exercise.
