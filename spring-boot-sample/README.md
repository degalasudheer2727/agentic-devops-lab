# Spring Boot order service

This sample creates and retrieves storefront orders. The request passes through Bean Validation and the shipping rule, then Spring Data JPA saves the order in H2. Orders at or above $50 ship free. Lower subtotals cost $5.99 to ship. All amounts are integer cents.

## Build and test

Use JDK 21, Maven 3.9+, and Python 3. For the promotion exercise, use Bash and GNU coreutils on Linux or WSL.

```bash
mvn -B -ntp -f spring-boot-sample/pom.xml clean verify
python3 spring-boot-sample/smoke.py spring-boot-sample/target/orders.jar
```

Integration tests use a real HTTP port and verify creation, persisted reads, threshold cases, validation, and missing orders. The smoke script launches the packaged JAR on a temporary port, exercises the API, and stops the process.

## Try the API

Run from the repository root. The service binds to localhost by default. This example uses a file-backed H2 database under an ignored directory so you can restart the process and retrieve the same order. The default configuration uses an in-memory database.

```bash
mkdir -p spring-boot-sample/data
java -jar spring-boot-sample/target/orders.jar \
  --spring.datasource.url=jdbc:h2:file:./spring-boot-sample/data/orders
```

In another shell:

```bash
curl --fail-with-body http://127.0.0.1:8080/actuator/health
curl --fail-with-body -i http://127.0.0.1:8080/api/orders \
  -H 'Content-Type: application/json' -d '{"subtotalCents":4999}'
```

Expect HTTP `201`, shipping of `599`, and a total of `5598`. Copy the `Location` URL from the response and GET it to retrieve the stored order. Try a subtotal of `5000` for free shipping and `-1` for a `400` response.

## Exercise the GitHub pipeline

1. In a branch, change the shipping rule from `>= 5000` to `> 5000`. Open a pull request and inspect the failing threshold case in **Verify Spring Boot service**. Restore the rule, rerun the check, then merge through review.
2. On `main`, open **Spring Boot Delivery**. The verify job uploads the tested JAR and passes its SHA-256 digest to the staging job.
3. If the `staging` environment has required reviewers, approve the job through GitHub. The staging job checks the digest, starts the downloaded JAR, tests health and order creation and retrieval, then activates the verified JAR in the runner sandbox.
4. For a local promotion or rollback, pass the retained JAR and its recorded digest to `bash spring-boot-sample/promote.sh <jar> <sha256> <staging-directory>`. A rejected digest or failed smoke test leaves `current.jar` untouched. Re-promote a previously verified artifact to rehearse rollback.

To run the promoted artifact locally, reserve a separate port and use a file-backed database:

```bash
checksum=$(sha256sum < spring-boot-sample/target/orders.jar)
bash spring-boot-sample/promote.sh spring-boot-sample/target/orders.jar "${checksum%% *}" staging/orders
java -jar staging/orders/current.jar --server.port=8081 \
  --spring.datasource.url=jdbc:h2:file:./staging/orders/data/orders
```

Repeat the API requests on port 8081. For a local rollback, stop the running service, re-promote the retained JAR with its known digest, and restart it against the same database. This exercise assumes both versions use the same schema.

The GitHub staging directory is ephemeral. For a persistent environment, use your runtime's deployment adapter, a managed database, schema migrations, and the same approval and artifact verification pattern described in the [operations runbook](../docs/operations.md).
