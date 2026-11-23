#!/usr/bin/env bash
set -euo pipefail

name=${1:?Specify trivy or gitleaks}
destination=${2:?Specify an installation directory}
case "$name" in
  trivy)
    url=https://github.com/aquasecurity/trivy/releases/download/v0.76.2/trivy_0.76.2_Linux-64bit.tar.gz
    digest=bc0fc726e017b8927a62b2d3531d7a84ee01769daf5c99ed866dced54089fdbf
    ;;
  gitleaks)
    url=https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz
    digest=551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb
    ;;
  *)
    echo "Unsupported scanner: $name" >&2
    exit 2
    ;;
esac

archive=$(mktemp)
trap 'rm -f -- "$archive"' EXIT
curl --fail --silent --show-error --location --retry 2 --max-time 60 "$url" --output "$archive"
printf '%s  %s\n' "$digest" "$archive" | sha256sum --check --strict
mkdir -p -- "$destination"
tar -xzf "$archive" -C "$destination" -- "$name"
