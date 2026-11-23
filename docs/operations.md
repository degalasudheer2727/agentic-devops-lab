# Environment setup and operations

## GitHub setup

1. Enable Actions in your sandbox repository. Run the workflow once to establish the check names.
2. Protect `main` with the checks in the [security control matrix](security-quality.md). Require PRs, review, and resolved conversations. Restrict creation and mutation of version tags to release maintainers.
3. Configure `staging` and `release` GitHub environments with the intended refs and required reviewers where supported. Test both a permitted and a rejected promotion.
4. Set repository Actions defaults to read-only and disable automatic PR approval. Enable native secret scanning, push protection, and Dependabot alerts where available.

## Adapt the deployment to your environment

The staging job smoke-tests the digest-verified image on a GitHub-hosted runner. Replace the sandbox deployment step with an adapter for your runtime. Verify artifact provenance, use a short-lived workload identity scoped to staging, keep credentials in your environment, and record which image digest is live. Use a managed database with approved schema migrations, TLS termination, and authentication before exposing the service.

## Release recovery

1. Record the failed run and active image digest. If the candidate failed before activation, keep the current deployment.
2. If the candidate was activated, select the previous attested digest. Review any migration compatibility before rollback.
3. Redeploy the verified previous digest through the same approval path. Record post-rollback API checks, runtime health, and the active digest.

## Agent operating policy

The agent works on one synthetic shipping regression in a temporary copy. It reads Surefire evidence, tries one allowlisted repair, and emits a patch only after Maven verification and HTTP smoke tests succeed. Maintainers review and merge through a PR. The agent workflow has read-only repository access. The optional model receives a fixed synthetic observation and returns an allowlisted decision.
