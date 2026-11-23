# GitHub releases and deployment

## Develop and review

1. Use the lab issue form to report a reproducible failure. Link the issue in a pull request and fill in the test checklist.
2. Review **Orders Service — Build, Scan, Stage, and Release**, **GitHub Workflows — Validate Syntax and Expressions**, **Maven Dependencies — Scan and Publish Vulnerability Alerts**, and **CodeQL — Scan Java, Python, and GitHub Actions** checks. Spring Boot HTTP integration results are downloadable from Actions. CodeQL analyzes Java, Python, and GitHub Actions on PRs, pushes to main, and a weekly schedule. Review alerts in the Security tab.
3. Review Dependabot updates like other PRs. The configuration tracks Maven, Actions, and the container base image.

Repository administrators can enforce these checks with a ruleset and configure required reviewers for the `staging` and `release` environments. The release workflow requires a version tag pointing to a commit reachable from `main`. Protect `v*` tags to restrict who can initiate a release. See the [operations runbook](operations.md) for stage setup.

## Publish a version from main

From a current checkout of `main`, select an unused version and push its tag.

```bash
git switch main
git pull --ff-only
git tag v1.0.1
git push origin v1.0.1
```

On a version tag, the release follows these gates.

| Stage | What must succeed |
| --- | --- |
| Build and source security | Maven tests and coverage, packaged service checks, Git history scan, and Dockerfile policy |
| Image qualification | Image vulnerability gate, HTTP smoke checks, and passive DAST |
| Candidate gate | The build, source security, and image qualification jobs all report success |
| Staging | Verify the archive digest and image ID, boot the candidate, run smoke checks, and record a staging receipt |
| Registry | After the release environment gate, verify the receipt, push the staged image, and attest the JAR and container |
| Independent verification | Verify release checksums and attestations, pull the GHCR image by digest, and confirm its image ID matches staging |
| GitHub Release | Publish the checked bundle only after independent verification succeeds |

The receipt binds the source commit, workflow run, archive digest, and image ID to the staging smoke result. The release contains `orders.jar`, `bom.json`, `SHA256SUMS`, `container-image.txt`, and `staging-receipt.json`. Pull requests and scheduled runs stop at candidate qualification. A push to `main` reaches staging. Only version tags can publish.

If registry verification fails, the image may already exist in GHCR, but the GitHub Release is withheld. Inspect the verification job and rerun failed jobs after fixing the cause. A successful rerun consumes the same run artifacts while they are retained.

## Verify and run a release

Run these commands in an empty directory. Choose a version with the current security gates in its release run.

```bash
repo=degalasudheer2727/agentic-devops-lab
read -r -p "Verified release tag: " version
gh release download "$version" --repo "$repo"
sha256sum --check SHA256SUMS
gh attestation verify orders.jar --repo "$repo"
image=$(cat container-image.txt)
gh attestation verify "oci://$image" --repo "$repo"
docker run --rm --publish 127.0.0.1:8080:8080 "$image"
```

If GHCR restricts the package, authenticate with a GitHub credential that has package read access. Run `curl -fsS http://127.0.0.1:8080/actuator/health` and use the [Spring Boot lab](../services/orders/README.md) to create and retrieve an order.

The staging environment runs on a GitHub-hosted runner and ends when its job completes. For a persistent deployment, run the verified digest in your own runtime with an external database. Keep the prior digest in the deployment record. To roll back, verify that prior digest, deploy it through the same approval path, and rerun the health and order smoke checks.
