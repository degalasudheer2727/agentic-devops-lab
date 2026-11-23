#!/usr/bin/env bash
set -euo pipefail

artifact=${1:?Specify a built zipapp}
expected=${2:?Specify the expected SHA-256}
target=${3:?Specify a staging directory}

actual=$(sha256sum < "$artifact")
if [[ ! $expected =~ ^[0-9a-f]{64}$ || ${actual%% *} != "$expected" ]]; then
  echo "Artifact digest mismatch" >&2
  exit 1
fi

mkdir -p "$target"
candidate=$(mktemp "$target/.candidate.XXXXXX")
trap 'rm -f "$candidate"' EXIT
cp "$artifact" "$candidate"
staged=$(sha256sum < "$candidate")
[[ ${staged%% *} == "$expected" ]]
[[ $(python "$candidate" 4999) == 599 ]]
[[ $(python "$candidate" 5000) == 0 ]]
mv -fT "$candidate" "$target/current.pyz"
echo "Promoted $expected"
