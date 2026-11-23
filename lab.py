"""Run a bounded, auditable repair loop against a synthetic CI regression."""

import argparse
import difflib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
CORRECT = "subtotal_cents >= 5000"
REGRESSION = "subtotal_cents > 5000"
FIX = "restore_inclusive_threshold"
ESCALATE = "escalate"
EXPECTED_FAILURE = "test_at_threshold (test_shipping.ShippingTests.test_at_threshold)"


def run_checks(directory):
    results = []
    for args in (["-m", "compileall", "-q", "."], ["-m", "unittest", "-v"]):
        result = subprocess.run(
            [sys.executable, *args], cwd=directory, capture_output=True,
            text=True, timeout=30, check=False,
        )
        results.append((result.returncode, result.stdout + result.stderr))
    return results


def decide(eligible, observation=(
    "Only test_at_threshold failed. Expected 0 at 5000 cents, "
    "observed 599. Runbook says >= 5000; fixture uses > 5000."
)):
    default = FIX if eligible else ESCALATE
    key = os.getenv("AI_GATEWAY_API_KEY")
    if not key:
        return default, "offline"
    if not eligible:
        return ESCALATE, "policy"
    # Send only a fixed synthetic observation, never local logs or source.
    body = {
        "model": "openai/gpt-4.1-mini",
        "messages": [
            {"role": "system", "content": (
                'Return JSON {"action":"restore_inclusive_threshold"} or '
                '{"action":"escalate"}. Only restore the threshold when '
                'shipping should be free at 5000 cents and the code uses >.'
            )},
            {"role": "user", "content": observation},
        ],
        "response_format": {"type": "json_object"},
    }
    request = Request(
        "https://ai-gateway.vercel.sh/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=15) as response:
            payload = json.loads(response.read(65536))
        action = json.loads(payload["choices"][0]["message"]["content"])["action"]
    except (ValueError, KeyError, IndexError, TypeError, URLError, TimeoutError):
        return ESCALATE, "model_error"
    return (action if action in (FIX, ESCALATE) else ESCALATE), "model"


def lab(scenario, output):
    output.mkdir(parents=True, exist_ok=False)
    original = (ROOT / "shipping.py").read_text()
    candidate = original
    if scenario == "regression":
        if original.count(CORRECT) != 1 or REGRESSION in original:
            raise ValueError("unexpected fixture source")
        candidate = original.replace(CORRECT, REGRESSION, 1)

    with TemporaryDirectory() as temp:
        directory = Path(temp)
        source = directory / "shipping.py"
        source.write_text(candidate)
        (directory / "test_shipping.py").write_text((ROOT / "test_shipping.py").read_text())
        build, tests = run_checks(directory)
        (output / "initial.log").write_text(build[1] + tests[1])
        failed = re.findall(r"^(?:FAIL|ERROR): (.+)$", tests[1], re.MULTILINE)
        eligible = (
            scenario == "regression" and build[0] == 0 and tests[0] == 1
            and failed == [EXPECTED_FAILURE] and "AssertionError: 599 != 0" in tests[1]
            and source.read_text() == candidate and candidate.count(REGRESSION) == 1
        )
        audit = {
            "scenario": scenario,
            "perceive": {"build_exit": build[0], "tests_exit": tests[0], "failures": failed},
            "reason": {"runbook": "free-shipping-threshold", "policy_eligible": eligible},
        }
        status = "healthy"
        if build[0] or tests[0]:
            action, mode = decide(eligible)
            audit["reason"].update({"decision": action, "mode": mode})
            status = "escalate"
            if eligible and action == FIX:
                repaired = candidate.replace(REGRESSION, CORRECT, 1)
                source.write_text(repaired)
                audit["act"] = {"file": "shipping.py", "attempts": 1}
                rebuilt, retested = run_checks(directory)
                (output / "verification.log").write_text(rebuilt[1] + retested[1])
                audit["verify"] = {"build_exit": rebuilt[0], "tests_exit": retested[0]}
                if rebuilt[0] == retested[0] == 0:
                    patch = difflib.unified_diff(
                        candidate.splitlines(keepends=True), repaired.splitlines(keepends=True),
                        "a/shipping.py", "b/shipping.py",
                    )
                    (output / "candidate.patch").write_text("".join(patch))
                    status = "verified_pending_review"

        audit["learn"] = {"outcome": status, "run_id": os.getenv("GITHUB_RUN_ID")}
        (output / "audit.json").write_text(json.dumps(audit, indent=2) + "\n")
        print(status)
        summary = os.getenv("GITHUB_STEP_SUMMARY")
        if summary:
            with Path(summary).open("a") as report:
                report.write(f"## Agentic DevOps Lab\n\nOutcome: `{status}`\n\n")
                report.write("See the run artifact for the audit, logs, and any verified patch.\n")
        return 1 if build[0] or tests[0] else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", choices=("healthy", "regression"))
    parser.add_argument("--output", type=Path, required=True)
    options = parser.parse_args()
    sys.exit(lab(options.scenario, options.output))
