"""Start a packaged Spring Boot service and verify its HTTP and database flow."""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def request(base, path, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = Request(base + path, data=data, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=5) as response:
            return response.status, json.load(response), response.headers
    except HTTPError as error:
        with error:
            return error.code, None, error.headers


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def check_service(base):
    status, health, headers = request(base, "/actuator/health")
    require(headers.get("X-Content-Type-Options") == "nosniff", "Missing nosniff header")
    require(headers.get("X-Frame-Options") == "DENY", "Framing protection missing")
    require("frame-ancestors 'none'" in headers.get("Content-Security-Policy", ""),
            "Content security policy missing")
    require(headers.get("Cache-Control") == "no-store", "Cache protection missing")
    require(status == 200 and health.get("status") == "UP", "Service is unhealthy")

    for subtotal, shipping in ((4999, 599), (5000, 0)):
        status, order, headers = request(base, "/api/orders", {"subtotalCents": subtotal})
        require(status == 201, f"Unexpected create status: {status}")
        path = "/api/orders/" + order["id"]
        require(headers["Location"] == base + path, "Unexpected Location header")
        require(order == {"id": order["id"], "subtotalCents": subtotal,
                          "shippingCents": shipping, "totalCents": subtotal + shipping},
                f"Incorrect totals: {order}")
        status, stored, _ = request(base, path)
        require(status == 200 and stored == order, "Stored order did not round-trip")
    status, _, _ = request(base, "/api/orders", {"subtotalCents": -1})
    require(status == 400, "Invalid order was accepted")
    status, _, _ = request(base, "/api/orders", {"subtotalCents": 1, "shippingCents": 0})
    require(status == 400, "Unexpected request field was accepted")
    status, _, _ = request(base, "/actuator/env")
    require(status == 404, "Unexpected management endpoint exposed")


def smoke(jar):
    with TemporaryDirectory() as directory:
        log = Path(directory) / "service.log"
        with log.open("wb") as output, subprocess.Popen(
            ["java", "-jar", str(jar.resolve()), "--server.port=0",
             "--spring.main.banner-mode=off"],
            cwd=directory, stdout=output, stderr=subprocess.STDOUT,
        ) as service:
            try:
                deadline = time.monotonic() + 45
                while time.monotonic() < deadline and service.poll() is None:
                    port = re.search(r"Tomcat started on port (\d+)", log.read_text(errors="replace"))
                    if port:
                        check_service("http://127.0.0.1:" + port[1])
                        print("Packaged service passed health, order lifecycle, and validation checks")
                        return
                    time.sleep(0.25)
                raise RuntimeError("The service did not start")
            except Exception:
                print(log.read_text(errors="replace"), file=sys.stderr)
                raise
            finally:
                if service.poll() is None:
                    service.terminate()
                    try:
                        service.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        service.kill()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("jar", nargs="?", type=Path)
    target.add_argument("--url", help="Base URL of an already running service")
    args = parser.parse_args()
    if args.url:
        check_service(args.url.rstrip("/"))
        print("Running service passed health, order lifecycle, and validation checks")
    else:
        smoke(args.jar)
