# Security and quality controls

| Control | Check and evidence |
| --- | --- |
| Source scanning | CodeQL runs the extended security query suite for Java and Python. Findings appear under **Security → Code scanning**. |
| Dependency alerts | **Dependency Security** scans resolved Maven dependencies from a CycloneDX SBOM. OSV findings appear in Code Scanning under the OSV category. The run summary includes a count and the SARIF and SBOM are retained for 30 days. A scanner or upload error fails the check. |
| Java quality | **Verify Spring Boot service** runs Maven integration tests and enforces at least 85% line coverage via JaCoCo. Download its test and coverage reports from the run. |
| Workflow quality | **Validate workflow syntax and expressions** checks all Actions YAML with a checksum-verified actionlint binary on PRs, main, and merge groups. |
| Trusted delivery | Actions are SHA-pinned. Job permissions default to none and are granted per job. Pull requests do not promote artifacts. Version tags still require a verified staging artifact before release publication. |

## Triage alerts

Use the Security tab to assign a finding and identify the affected code or dependency. For dependencies, compare the SBOM to the affected component and update the dependency through a pull request. Keep exceptions scoped, time-limited, and linked to the review record. Scanner findings are reported through Code Scanning. The dependency scan job reports whether the scan and upload completed.

## Repository settings for an administrator

In **Settings → Advanced Security**, enable Dependabot alerts, Dependabot security updates, secret scanning, and push protection if available to your repository. Dependabot version updates are configured in the repository. Review notification preferences to route security alerts to the maintainers.

In **Settings → Rules → Rulesets**, protect `main` and select the stable check names after they appear on a PR. At minimum, require **Verify Spring Boot service**, **Validate and package**, **Validate workflow syntax and expressions**, and the two CodeQL language checks. The dependency scan runs on relevant PR paths and should be evaluated separately from always-running required checks. Restrict creation of release tags to authorized maintainers.

Set repository Actions defaults to read-only and disable approval of pull requests by GitHub Actions. Configure environment reviewers and deployment branch/tag restrictions for `staging` and `release`. The workflow job permissions and environment references are defined in code, while repository-wide permissions, reviewer requirements, and ruleset enforcement are administrator settings.
