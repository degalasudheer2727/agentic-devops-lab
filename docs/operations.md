# Environment setup and operations

## GitHub sandbox setup

1. Push the source to a sandbox repository with GitHub Actions enabled. The first **Delivery** run establishes the check name.
2. Protect `main` with a ruleset. Require PRs, at least one approval, and the **Validate and package** check. Also require **Verify Spring Boot service** once its first run establishes the check. Block force pushes and deletions. Consider CODEOWNERS review for workflow and policy changes, using your real teams.
3. Configure a GitHub environment named `staging` with `main` as its deployment branch. Add required reviewers and prevent self-review where your plan supports those settings. These are repository settings. Creating an environment from workflow YAML alone establishes no approval requirement.
4. Run the labs. Confirm a failing PR cannot merge, a staging job waits when reviewers are configured, and the release artifact name and SHA-256 match the run summary.

## Delivery controls

| Control | Reference implementation |
| --- | --- |
| Permissions | Read-only source checkout with persisted credentials disabled. PRs use `pull_request` and receive no deployment credentials. |
| Dependencies | Actions are pinned by commit. Review updates through PRs. The sample application uses the Python standard library. |
| Integrity | The staging job promotes the candidate from the same run and checks it against the trusted build job output. |
| Verification | Unit tests gate packaging. Staging runs boundary smoke checks before replacing the previous artifact. |
| Approval | The GitHub environment can gate staging. A maintainer reviews agent-generated patches through the ordinary PR process. |
| Evidence | Retain release artifacts for 14 days and repair results for 7 days by default. Capture the commit, digest, run ID, and review record for longer retention. |

## Adapt to a real staging target

The hosted staging job uses an ephemeral directory to demonstrate the promotion contract. For a persistent target, replace that job's staging command with an adapter for your runtime. Keep the existing job dependency, environment gate, digest check, and smoke checks. Pass the artifact to the target using the target's normal release mechanism. Run readiness checks in an inactive slot before switching traffic.

Use short-lived workload identity for the deployment job if your provider supports OIDC. Limit the provider trust policy to the intended repository and staging environment. Give the identity permission only for the intended staging resources. Scope secrets to the environment and keep the optional model key isolated from delivery jobs.

Before a production rollout, use protected environments, an artifact store with an appropriate retention policy, and signed provenance verified by the deployer. The in-run SHA-256 check proves byte consistency between jobs. Provenance is needed to independently verify who built a release and from which source. Add dependency, image, and secret scanning appropriate to your stack and enforce findings through the release policy.

## Release recovery runbook

1. Pause promotion and record the failed run, current commit and digest, and relevant smoke output.
2. If validation failed before activation, keep the currently active release. Correct the cause through a PR.
3. If the release was activated and later regressed, identify the prior known-good artifact and digest from the release record. Re-promote those exact bytes using the same approval path. The local rollback exercise shows this with `scripts/promote.sh`.
4. Verify the target's health, confirm the active digest, and record the rollback outcome. For data migrations, follow the application's migration-specific recovery procedure.

## Agent operating policy

The model chooses between one allowlisted repair and escalation. The offline policy handles the same known synthetic case. Unexpected failures and provider errors reach a human. The agent has one attempt, a temporary workspace, no repository write token, and no deploy interface. For adoption, start with read-only triage and measure time to diagnosis, verified proposal rate, and rejected proposals before expanding the action policy.
