from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Dataset:
    name: str
    x: list[float]
    y: list[float]
    dx: list[float] | None = None
    dy: list[float] | None = None
    line_width: float = 2.0
    line_style: str = "-"
    line_color: str = "black"
    marker: str = "None"
    marker_size: float = 6.0
    marker_face_color: str = "black"
    marker_edge_color: str = "black"
    marker_fill: bool = False


DEFAULT_COLORS = [
    "black",
    "red",
    "blue",
    "purple",
    "green",
    "magenta",
    "cyan",
    "orange",
    "brown",
]


def _parse_xy_lines(lines: list[str]) -> tuple[list[float], list[float]]:
    # Backward-compatible helper used by tests and older call paths.
    x: list[float] = []
    y: list[float] = []
    for row in _parse_numeric_rows(lines):
        if len(row) < 2:
            continue
        x.append(row[0])
        y.append(row[1])
    return x, y


def _parse_bxy_spec(spec: str) -> tuple[int, int, int | None, int | None]:
    parts = [part.strip() for part in spec.split(":") if part.strip()]
    if len(parts) not in {2, 3, 4}:
        raise ValueError("bxy spec must be x:y, x:y:dy, or x:y:dx:dy")

    try:
        indices = [int(part) for part in parts]
    except ValueError as exc:
        raise ValueError("bxy spec indices must be integers") from exc

    if any(idx <= 0 for idx in indices):
        raise ValueError("bxy spec indices must be >= 1")

    x_idx = indices[0] - 1
    y_idx = indices[1] - 1
    dx_idx: int | None = None
    dy_idx: int | None = None

    if len(indices) == 3:
        dy_idx = indices[2] - 1
    if len(indices) == 4:
        dx_idx = indices[2] - 1
        dy_idx = indices[3] - 1

    return x_idx, y_idx, dx_idx, dy_idx


def _split_row_tokens(stripped: str) -> list[str]:
    if "," in stripped:
        row = next(csv.reader([stripped]))
        return [cell.strip() for cell in row if cell.strip()]
    return stripped.split()


def _parse_numeric_rows(lines: list[str]) -> list[list[float]]:
    rows: list[list[float]] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#") or stripped.startswith("@"):
            continue

        parts = _split_row_tokens(stripped)
        if len(parts) < 2:
            continue

        try:
            row = [float(part) for part in parts]
        except ValueError:
            continue
        rows.append(row)
    return rows


def _extract_columns(rows: list[list[float]], indices: tuple[int, int, int | None, int | None]) -> tuple[list[float], list[float], list[float] | None, list[float] | None]:
    x_idx, y_idx, dx_idx, dy_idx = indices
    x: list[float] = []
    y: list[float] = []
    dx: list[float] | None = [] if dx_idx is not None else None
    dy: list[float] | None = [] if dy_idx is not None else None

    for row in rows:
        required = [x_idx, y_idx]
        if dx_idx is not None:
            required.append(dx_idx)
        if dy_idx is not None:
            required.append(dy_idx)
        if max(required) >= len(row):
            continue

        x.append(row[x_idx])
        y.append(row[y_idx])
        if dx_idx is not None and dx is not None:
            dx.append(row[dx_idx])
        if dy_idx is not None and dy is not None:
            dy.append(row[dy_idx])

    return x, y, dx, dy


def load_datasets(paths: list[Path], bxy_specs: list[str | None] | None = None) -> list[Dataset]:
    datasets: list[Dataset] = []
    color_idx = 0

    normalized_specs = bxy_specs or []

    for file_idx, path in enumerate(paths):
        if not path.exists():
            continue

        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        rows = _parse_numeric_rows(lines)
        if not rows:
            continue

        spec = normalized_specs[file_idx] if file_idx < len(normalized_specs) else None

        if spec:
            indices = _parse_bxy_spec(spec)
            x, y, dx, dy = _extract_columns(rows, indices)
            if not x:
                continue
            color = DEFAULT_COLORS[color_idx % len(DEFAULT_COLORS)]
            color_idx += 1
            datasets.append(
                Dataset(
                    name=path.name,
                    x=x,
                    y=y,
                    dx=dx,
                    dy=dy,
                    line_color=color,
                    marker_face_color=color,
                    marker_edge_color=color,
                )
            )
            continue

        min_cols = min(len(row) for row in rows)
        if min_cols < 2:
            continue

        # Default behavior for multi-column files: first column is X, each remaining column is a Y set.
        for y_idx in range(1, min_cols):
            x, y, _dx, _dy = _extract_columns(rows, (0, y_idx, None, None))
            if not x:
                continue
            color = DEFAULT_COLORS[color_idx % len(DEFAULT_COLORS)]
            color_idx += 1
            name = path.name if y_idx == 1 else f"{path.name}:col{y_idx + 1}"
            datasets.append(
                Dataset(
                    name=name,
                    x=x,
                    y=y,
                    line_color=color,
                    marker_face_color=color,
                    marker_edge_color=color,
                )
            )

    return datasets
