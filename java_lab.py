"""Run the agent repair exercise against the Spring Boot sample."""

import argparse
import difflib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET

from lab import FIX, decide


ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / "spring-boot-sample"
FILE = Path("src/main/java/dev/lab/orders/StoreOrder.java")
EXPECTED = "dev.lab.orders.OrdersApiTest#offersFreeShippingAtThreshold"
CORRECT = "subtotalCents >= 5000"
REGRESSION = "subtotalCents > 5000"
OBSERVATION = (
    "Only the Java HTTP integration test offersFreeShippingAtThreshold failed. "
    "Expected 0 at 5000 cents, observed 599. The shipping runbook says >= 5000 "
    "and the synthetic Java fixture uses > 5000."
)


def run(command, directory, log, timeout):
    environment = os.environ.copy()
    environment.pop("AI_GATEWAY_API_KEY", None)
    with log.open("wb") as output:
        try:
            return subprocess.run(
                command, cwd=directory, stdout=output, stderr=subprocess.STDOUT,
                timeout=timeout, check=False, env=environment,
            ).returncode
        except subprocess.TimeoutExpired:
            output.write(b"\nCommand exceeded its time limit.\n")
            return 124
        except FileNotFoundError as error:
            output.write(f"{error}\n".encode())
            return 127


def test_result(directory):
    issues = []
    for report in sorted(directory.glob("target/surefire-reports/TEST-*.xml")):
        for case in ET.parse(report).getroot().findall("testcase"):
            for tag in ("failure", "error"):
                issue = case.find(tag)
                if issue is not None:
                    issues.append({
                        "test": f"{case.get('classname')}#{case.get('name')}",
                        "kind": tag,
                        "message": issue.get("message", ""),
                    })
    return issues


def exercise(scenario, mode, output, maven):
    output.mkdir(parents=True, exist_ok=False)
    command = [*maven, "-B", "-ntp"]
    with TemporaryDirectory(prefix="orders-agent-") as scratch:
        directory = Path(scratch)
        shutil.copy2(PROJECT / "pom.xml", directory)
        shutil.copytree(PROJECT / "src", directory / "src")
        source = directory / FILE
        baseline = source.read_text()
        candidate = baseline
        if scenario == "regression" and baseline.count(CORRECT) == 1:
            candidate = baseline.replace(CORRECT, REGRESSION, 1)
            source.write_text(candidate)
        initial = run(command + ["test"], directory, output / "initial.log", 300)
        try:
            issues = test_result(directory)
            reports_valid = True
        except ET.ParseError:
            issues = []
            reports_valid = False
        eligible = (
            scenario == "regression" and initial == 1 and reports_valid
            and len(issues) == 1 and issues[0]["test"] == EXPECTED
            and issues[0]["kind"] == "failure"
            and "expected: 0" in issues[0]["message"]
            and "but was: 599" in issues[0]["message"]
            and source.read_text() == candidate and candidate.count(REGRESSION) == 1
            and baseline != candidate
        )
        audit = {
            "scenario": scenario,
            "mode": mode,
            "perceive": {
                "test_exit": initial,
                "reports_valid": reports_valid,
                "issues": [{"test": item["test"], "kind": item["kind"]} for item in issues],
            },
            "reason": {"runbook": "free-shipping-threshold", "eligible": eligible},
            "act": {"attempts": 0},
        }
        outcome = "healthy" if initial == 0 and scenario == "healthy" else "escalate"
        if eligible and mode == "observe":
            outcome = "diagnosed"
        if eligible and mode == "repair":
            action, decision_mode = decide(True, OBSERVATION)
            audit["reason"].update(decision=action, decision_mode=decision_mode)
            if action == FIX:
                source.write_text(baseline)
                audit["act"] = {"attempts": 1, "path": str(Path(PROJECT.name) / FILE)}
                build = run(command + ["clean", "verify"], directory, output / "verification.log", 300)
                smoke = None
                if build == 0:
                    smoke = run(
                        [sys.executable, str(PROJECT / "smoke.py"),
                         str(directory / "target/orders.jar")],
                        directory, output / "smoke.log", 90,
                    )
                audit["verify"] = {"maven_exit": build, "smoke_exit": smoke}
                if build == 0 and smoke == 0:
                    path = f"{PROJECT.name}/{FILE.as_posix()}"
                    patch = difflib.unified_diff(
                        candidate.splitlines(keepends=True), baseline.splitlines(keepends=True),
                        f"a/{path}", f"b/{path}",
                    )
                    (output / "candidate.patch").write_text("".join(patch))
                    outcome = "verified_pending_review"

    audit["learn"] = {"outcome": outcome, "run_id": os.getenv("GITHUB_RUN_ID")}
    (output / "audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(outcome)
    summary = os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with Path(summary).open("a") as report:
            report.write(f"## Spring Boot agent lab\n\nOutcome: `{outcome}`\n\n")
            report.write("Download the run evidence for the audit, logs, and verified patch.\n")
    return 0 if outcome == "healthy" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", choices=("healthy", "regression"))
    parser.add_argument("--mode", choices=("observe", "repair"), default="repair")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--maven", default="mvn")
    parser.add_argument("--maven-settings", type=Path)
    args = parser.parse_args()
    maven = [args.maven]
    if args.maven_settings:
        maven += ["--settings", str(args.maven_settings.resolve())]
    sys.exit(exercise(args.scenario, args.mode, args.output, maven))
