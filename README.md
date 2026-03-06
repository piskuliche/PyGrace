# PyGrace

PyGrace is an XMGrace-inspired plotting tool built on Matplotlib with a Qt GUI.
It supports quick CLI plotting, interactive plot editing, and PNG hardcopy export.

## Features

- XMGrace-like CLI (`xmgrace`) with familiar flags (`-nxy`, `-bxy`, `-title`, `-world`, `-legend`, `-hardcopy`, etc.)
- Reads whitespace-delimited and CSV numeric data
- Multi-column loading: first column is X, each remaining column is a separate Y series
- Error bar plotting via `-bxy x:y:dy` or `-bxy x:y:dx:dy`
- Interactive GUI controls for labels, axis limits, tick spacing, dataset visibility, and appearance
- Transform expressions for derived data (for example: `y1 = y0 * 2`)
- Plugin overlays including `y = x` shading and linear regression
- Headless PNG rendering for batch workflows

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .[dev]
```

Quick setup script:

```bash
./scripts/dev_setup.sh
```

## Quick Start

Open the GUI with one or more data files:

```bash
xmgrace examples/data/rising.dat examples/data/falling.dat
```

Use explicit XY mode:

```bash
xmgrace -nxy examples/data/rising.dat -nxy examples/data/bowl.dat
```

Set labels and bounds:

```bash
xmgrace -title "Demo" -xlabel "Time" -ylabel "Value" -world 0 10 -1 5 examples/data/rising.dat
```

Load error bars by column mapping (1-based):

```bash
xmgrace -nxy examples/data/errorbars_xy.dat -bxy 1:2:3:4
```

Render directly to PNG (no GUI):

```bash
xmgrace -hardcopy -device PNG -printfile out.png examples/data/bowl.dat
```

## Data Format Notes

- Lines starting with `#` or `@` are ignored.
- Non-numeric lines are skipped.
- CSV and whitespace-delimited rows are both supported.
- Without `-bxy`, the loader treats column 1 as X and columns 2..N as separate Y datasets.
- `-bxy` forms:
  - `x:y`
  - `x:y:dy`
  - `x:y:dx:dy`

## Example Commands

```bash
./examples/open_example_plot.sh
./examples/open_errorbar_plot.sh
```

## Development

Run tests:

```bash
pytest
```

Run as a module:

```bash
python -m pygrace examples/data/rising.dat
```

## Repository Layout

```text
.
├── examples/        # sample data and runnable demos
├── scripts/         # local developer setup helpers
├── src/pygrace/     # package source
└── tests/           # test suite
```

## Current Limitations

- Hardcopy currently supports `PNG` output only.
- Unsupported CLI flags are ignored with a warning.
