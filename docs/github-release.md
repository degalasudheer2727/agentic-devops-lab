# GitHub releases and deployment

## Develop and review

1. Use the lab issue form to report a reproducible failure. Link the issue in a pull request and fill in the test checklist.
2. Review **Spring Boot Delivery**, **Workflow Quality**, **Dependency Security**, and **CodeQL** checks. Spring Boot HTTP integration results are downloadable from Actions. CodeQL analyzes Java, Python, and GitHub Actions on PRs, pushes to main, and a weekly schedule. Review alerts in the Security tab.
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

On a version tag, the pipeline tests the JAR and publishes the staged bytes as `orders.jar`, along with `bom.json`, `SHA256SUMS`, and `container-image.txt`. It builds the non-root container once, scans and tests it, then verifies and reuses the same image archive in staging and release. GHCR receives the tested image. GitHub records provenance attestations for the JAR and the container digest. The GitHub Release is created after the image and attestations succeed.

## Verify and run a release

Run these commands in an empty directory. Use a version that is listed in GitHub Releases.

```bash
repo=degalasudheer2727/agentic-devops-lab
version=v1.0.0
gh release download "$version" --repo "$repo"
sha256sum --check SHA256SUMS
gh attestation verify orders.jar --repo "$repo"
image=$(cat container-image.txt)
gh attestation verify "oci://$image" --repo "$repo"
docker run --rm --publish 127.0.0.1:8080:8080 "$image"
```

If GHCR restricts the package, authenticate with a GitHub credential that has package read access. Run `curl -fsS http://127.0.0.1:8080/actuator/health` and use the [Spring Boot lab](../services/orders/README.md) to create and retrieve an order.

The staging environment runs on a GitHub-hosted runner and ends when its job completes. For a persistent deployment, run the verified digest in your own runtime with an external database. Keep the prior digest in the deployment record. To roll back, verify that prior digest, deploy it through the same approval path, and rerun the health and order smoke checks.
