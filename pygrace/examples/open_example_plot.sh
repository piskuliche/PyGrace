#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="$ROOT_DIR/.venv/bin/python"

if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi

export PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"

exec "$PYTHON_BIN" -m pygrace.cli \
  -title "PyGrace Example Plot" \
  -xlabel "X" \
  -ylabel "Y" \
  -legend "rising,falling,bowl" \
  -nxy "$ROOT_DIR/examples/data/rising.dat" \
  -nxy "$ROOT_DIR/examples/data/falling.dat" \
  -nxy "$ROOT_DIR/examples/data/bowl.dat"
