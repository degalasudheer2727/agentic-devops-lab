#!/usr/bin/env bash
set -euo pipefail

output=${1:?Specify an output path}
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT
cp shipping.py "$scratch/shipping.py"
cat > "$scratch/__main__.py" <<'PY'
import argparse

from shipping import shipping_cost

parser = argparse.ArgumentParser(description="Calculate shipping in cents.")
parser.add_argument("subtotal_cents", type=int)
args = parser.parse_args()
print(shipping_cost(args.subtotal_cents))
PY
mkdir -p "$(dirname "$output")"
python -m zipapp "$scratch" --output "$output"
