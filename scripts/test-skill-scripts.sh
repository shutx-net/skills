#!/bin/sh
# Run the tests for scripts bundled with skills.
#
# Tests live in tests/<skill-name>/test_*.py, outside skills/ so they stay out
# of the distributed packages. Each directory runs with the Python standard
# library's unittest discovery.
#
# Usage: ./scripts/test-skill-scripts.sh
#
# Requires: POSIX sh and python3 (set PYTHON to use another interpreter).

set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

PYTHON=${PYTHON:-python3}
# Don't leave __pycache__ directories in the working tree.
PYTHONDONTWRITEBYTECODE=1
export PYTHONDONTWRITEBYTECODE

status=0
found=0
for dir in tests/*/; do
	[ -d "$dir" ] || continue
	found=1
	printf 'Testing %s\n' "$dir"
	"$PYTHON" -m unittest discover -s "$dir" -p 'test_*.py' || status=1
done

if [ "$found" -eq 0 ]; then
	printf 'No tests found in tests/*/\n'
fi
exit "$status"
