# Security and quality controls

| Control | Evidence and enforcement |
| --- | --- |
| Source and workflow scanning | CodeQL checks Java, Python, and Actions. Findings are published to Code Scanning. |
| Secret detection | Gitleaks scans committed history in the checked-out revision with redacted output. Findings block the delivery candidate. |
| Software composition | CycloneDX records resolved Maven packages. OSV publishes dependency findings to Code Scanning on main, relevant PRs, and a schedule. |
| Container configuration | Trivy checks the Dockerfile and fails the candidate for high or critical configuration findings. |
| Container vulnerabilities | Trivy records OS and application findings at every severity, including on a weekly rescan. A fixable high or critical finding blocks staging and release. Unfixed findings still require review. |
| Build quality | Maven runs real HTTP integration tests and enforces at least 85% line coverage. Actionlint validates workflow syntax and expressions. |
| Runtime security | The candidate runs as non-root with no capabilities, a read-only root filesystem, and a loopback-only published port. Smoke tests exercise API validation, headers, data persistence, and management endpoint exposure. |
| Dynamic scanning | A digest-pinned OWASP ZAP baseline scans the temporary health endpoint passively and publishes its report. API smoke tests cover the order routes. |
| Supply chain | SHA-pinned actions, checksum-verified scanners, digest-pinned base image, a verified JAR, and a verified image archive. A separate read-only job verifies the staged receipt, registry image identity, and attestations before GitHub publishes a release. |
| Change governance | Administrators configure PR rulesets, release tag protection, environment approvals, and organization alert routing. |

## Audit evidence

| Practice | Evidence to retain |
| --- | --- |
| Secure development and verification (NIST SSDF PW) | PR review, coverage, CodeQL, secret scan, image policy, and passive scan results |
| Vulnerability response (NIST SSDF RV) | SBOM, Code Scanning alert, affected version, and tracked remediation or approved exception |
| Release integrity (NIST SSDF PS and SLSA provenance) | Git revision, artifact SHA-256, published image digest, attestation, and staging run |
| Runtime verification (OWASP ASVS) | HTTP validation and security header checks, plus access-control and TLS evidence from the target deployment |

## Triage and administrator settings

Review **Security → Code scanning** and the Actions artifacts. For each finding, record the affected version, severity, owner, due date, and fix or exception in your change record. Keep exceptions time-limited and approved.

Protect `main` using checks from **Orders Service — Build, Scan, Stage, and Release**, **GitHub Workflows — Validate Syntax and Expressions**, and all three CodeQL language jobs. Replace any earlier required check named **Validate and package**, which belonged to the retired Python sample. Require a pull request and resolved review conversations. Add reviewer requirements based on your team and use the Code Scanning merge rule for your chosen severity threshold. Configure native Dependabot alerts, secret scanning, and push protection where available, along with the `staging` and `release` environment gates.

These controls can support secure development and audit evidence. Certification or compliance depends on the applicable standard, the deployment environment, organization policies, and evidence reviewed by the accountable team.
