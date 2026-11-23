# Hands-on labs

Start with the [Spring Boot agent workbook](java-agent-lab.md) for the primary exercise. Run the companion labs below from the repository root. Use Python 3.12+, Bash, Git, and Linux or WSL with GNU coreutils. Labs 2–4 run without a GitHub account or API key.

## 1. Break a pull request check and fix it

1. In your sandbox repository, create a branch and change `>= 5000` to `> 5000` in `shipping.py`.
2. Run `python -m unittest -v`. Expect only `test_at_threshold` to fail.
3. Push the branch and open a pull request. Confirm **Validate and package** fails and the staging job is skipped. Restore the inclusive comparison and push again. Confirm the PR check passes before requesting review.
4. With branch protection configured, merge through the PR. Open the **Delivery** run on `main`, inspect the candidate artifact, and approve the staging job if required. Verify the job summary records the digest and commit.

## 2. Build once and promote the same artifact

```bash
scratch=$(mktemp -d)
mkdir -p "$scratch/v1" "$scratch/v2"
bash scripts/build.sh "$scratch/v1/shipping.pyz"
digest1=$(sha256sum < "$scratch/v1/shipping.pyz")
digest1=${digest1%% *}
bash scripts/promote.sh "$scratch/v1/shipping.pyz" "$digest1" "$scratch/staging"
python "$scratch/staging/current.pyz" 5000
```

The staging command prints the promoted digest. The CLI prints `0`, demonstrating free shipping at the threshold.

## 3. Reject a bad artifact and rehearse rollback

Continue in the same shell. Build a harmless second release by changing only its CLI help description, while leaving the shipping checks intact.

```bash
mkdir "$scratch/v2/source"
python -m zipfile -e "$scratch/v1/shipping.pyz" "$scratch/v2/source"
sed -i 's/Calculate shipping in cents/Calculate storefront shipping/' "$scratch/v2/source/__main__.py"
python -m zipapp "$scratch/v2/source" -o "$scratch/v2/shipping.pyz"
digest2=$(sha256sum < "$scratch/v2/shipping.pyz")
digest2=${digest2%% *}

# Expected failure. The checksum still points to v1.
bash scripts/promote.sh "$scratch/v2/shipping.pyz" "$digest1" "$scratch/staging"
sha256sum "$scratch/staging/current.pyz"

# Promote v2, then restore v1 from the retained artifact.
bash scripts/promote.sh "$scratch/v2/shipping.pyz" "$digest2" "$scratch/staging"
bash scripts/promote.sh "$scratch/v1/shipping.pyz" "$digest1" "$scratch/staging"
sha256sum "$scratch/staging/current.pyz"
```

Both SHA-256 checks of `current.pyz` should show the v1 digest. To practice smoke-test failure, rebuild the candidate with the exclusive threshold in the extracted v2 source, compute its correct digest, and verify that promotion still fails and v1 stays active.

## 4. Investigate an agent repair

Run `python lab.py regression --output "$scratch/repair"` with a fresh output path. The deliberate test failure returns exit 1, even though verification of the temporary repair succeeds.

- Compare `initial.log` and `verification.log`.
- Inspect `audit.json` for the failed check, policy decision, verification exit codes, and `verified_pending_review` outcome.
- Review `candidate.patch`. To apply it on a disposable branch containing the actual boundary bug, run `git apply --check /path/to/candidate.patch`, apply it, repeat the tests, and open a PR for human review.
- Try a second failure by changing the below-threshold assertion in a disposable copy. The agent should return `escalate` and produce no patch. Restore the assertion afterward.

In GitHub, run the manual **Agentic DevOps Lab** workflow on `main` and download `lab-evidence` to repeat the review. The offline policy is the default. To compare the model decision, configure the optional Actions secret described in the README and submit a fresh run.

## 5. Deliver a Spring Boot service

Follow the [Spring Boot lab](../spring-boot-sample/README.md) to build and test an order API, break and restore a pull request check, inspect the packaged JAR and its digest, and repeat staging promotion or rollback locally.
