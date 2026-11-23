#!/usr/bin/env bash
set -euo pipefail

artifact=${1:?Specify the built service JAR}
expected=${2:?Specify the expected SHA-256}
target=${3:?Specify the staging directory}
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

if [[ ! $expected =~ ^[0-9a-f]{64}$ ]]; then
  echo 'Expected a lowercase SHA-256 digest' >&2
  exit 1
fi

mkdir -p "$target"
candidate=$(mktemp "$target/.candidate.XXXXXX")
trap 'rm -f -- "$candidate"' EXIT
cp -- "$artifact" "$candidate"
actual=$(sha256sum < "$candidate")
if [[ ${actual%% *} != "$expected" ]]; then
  echo 'Artifact digest mismatch' >&2
  exit 1
fi

python3 "$script_dir/smoke.py" "$candidate"
mv -fT -- "$candidate" "$target/current.jar"
echo "Promoted Spring Boot JAR $expected"
