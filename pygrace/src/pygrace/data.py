from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Dataset:
    name: str
    x: list[float]
    y: list[float]
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
    x: list[float] = []
    y: list[float] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#") or stripped.startswith("@"):  # ignore comments/commands
            continue
        parts = stripped.split()
        if len(parts) < 2:
            continue
        try:
            xv = float(parts[0])
            yv = float(parts[1])
        except ValueError:
            continue
        x.append(xv)
        y.append(yv)
    return x, y


def load_datasets(paths: list[Path]) -> list[Dataset]:
    datasets: list[Dataset] = []
    for idx, path in enumerate(paths):
        if not path.exists():
            continue
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        x, y = _parse_xy_lines(lines)
        if not x:
            continue
        color = DEFAULT_COLORS[idx % len(DEFAULT_COLORS)]
        datasets.append(
            Dataset(
                name=path.name,
                x=x,
                y=y,
                line_color=color,
                marker_face_color=color,
                marker_edge_color=color,
            )
        )
    return datasets
