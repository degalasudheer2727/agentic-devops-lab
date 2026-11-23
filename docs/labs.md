# Hands-on labs

Use JDK 21, Maven 3.9+, Python 3.12+, Git, and Bash from the repository root. Docker is needed for the image exercises.

## 1. Break and repair a PR check

In a branch of your sandbox repository, change `>= 5000` to `> 5000` in `services/orders/src/main/java/dev/lab/orders/StoreOrder.java`. Run `mvn -f services/orders/pom.xml test` and open a pull request. Verify the threshold test fails and the image job is blocked. Restore the comparison or apply a patch from the [agent exercise](java-agent-lab.md). Confirm CI succeeds before merging.

## 2. Scan and run the delivery candidate

```bash
mvn -B -ntp -f services/orders/pom.xml clean verify
docker build -f services/orders/Dockerfile -t orders:lab services/orders/target
bash tools/ci/smoke-container.sh orders:lab
```

Check that the container runs with a read-only filesystem, no Linux capabilities, and a loopback-only published port. The smoke script checks health, persistence, input validation, exposed endpoints, and security headers.

## 3. Review security findings

Open a **Maven Dependencies — Scan and Publish Vulnerability Alerts** run and inspect the summary, SARIF, and SBOM. Locate the same rule in GitHub Code Scanning. In **Orders Service — Build, Scan, Stage, and Release**, inspect the image security report. Use the affected package, fixed version, and source to determine whether the fix belongs in Maven or the base image. Retest the revised dependency or image digest on a PR.

## 4. Rehearse a rejected artifact and rollback

Continue with the [Spring Boot service guide](../services/orders/README.md) to demonstrate local artifact verification. Pass an incorrect checksum and confirm the existing JAR stays in place. For container rollback, use the previous attested image by digest and rerun the smoke checks. Record both digests and link the release evidence in the change record.
