#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="$ROOT_DIR/.venv/bin/python"

if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi

export PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"

exec "$PYTHON_BIN" -m pygrace.cli \
  -title "PyGrace Errorbar Demo" \
  -xlabel "X" \
  -ylabel "Y" \
  -legend "y+dy,xy+dx+dy" \
  -nxy "$ROOT_DIR/examples/data/errorbars_y.dat" \
  -nxy "$ROOT_DIR/examples/data/errorbars_xy.dat" \
  --bxy 1:2:3 \
  --bxy 1:2:3:4
