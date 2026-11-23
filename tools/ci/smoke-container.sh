#!/usr/bin/env bash
set -euo pipefail

image=${1:?Specify the orders image}
id=$(docker run --detach --read-only --tmpfs /tmp:rw,nosuid,nodev \
  --cap-drop ALL --security-opt no-new-privileges --publish 127.0.0.1::8080 "$image")
trap 'docker logs "$id" >&2; docker rm -f "$id" >/dev/null' EXIT
address=$(docker port "$id" 8080/tcp)
curl --fail --silent --show-error --retry 15 --retry-all-errors \
  --retry-max-time 50 --max-time 5 "http://$address/actuator/health" >/dev/null
python3 services/orders/smoke.py --url "http://$address"

if [[ $# -ge 2 ]]; then
  report_dir=$2
  mkdir -p -- "$report_dir"
  # The pinned scanner writes the report as its unprivileged container user.
  chmod a+w -- "$report_dir"
  docker run --rm --network host \
    --volume "$report_dir:/zap/wrk:rw" \
    ghcr.io/zaproxy/zaproxy@sha256:9624669db72f54d86c4b46a7064518bd9bf79d8c61a4c31befa9923489f328af \
    zap-baseline.py -t "http://$address/actuator/health" -m 1 -I -J zap.json
  test -s "$report_dir/zap.json"
fi
