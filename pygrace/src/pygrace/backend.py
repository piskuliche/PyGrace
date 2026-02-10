from __future__ import annotations

import ast
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib
from matplotlib import ticker

from .data import Dataset
from .plugins import PLUGIN_DEFINITIONS, PLUGIN_LIST, Y_EQUALS_X_PLUGIN_ID


@dataclass
class PlotState:
    title: str | None
    xlabel: str | None
    ylabel: str | None
    world: list[float] | None
    autoscale: bool
    title_size: float | None = None
    xlabel_size: float | None = None
    ylabel_size: float | None = None
    xtick_size: float | None = None
    ytick_size: float | None = None
    x_major_step: float | None = None
    y_major_step: float | None = None
    x_minor_step: float | None = None
    y_minor_step: float | None = None
    minor_ticks: bool = False


class Vec:
    def __init__(self, values: list[float]):
        self.values = values

    def _binary(self, other, op):
        if isinstance(other, Vec):
            if len(self.values) != len(other.values):
                raise ValueError("Vector length mismatch")
            return Vec([op(a, b) for a, b in zip(self.values, other.values)])
        return Vec([op(a, float(other)) for a in self.values])

    def __add__(self, other):
        return self._binary(other, lambda a, b: a + b)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self._binary(other, lambda a, b: a - b)

    def __rsub__(self, other):
        if isinstance(other, Vec):
            return other.__sub__(self)
        return Vec([float(other) - a for a in self.values])

    def __mul__(self, other):
        return self._binary(other, lambda a, b: a * b)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        return self._binary(other, lambda a, b: a / b)

    def __rtruediv__(self, other):
        if isinstance(other, Vec):
            return other.__truediv__(self)
        return Vec([float(other) / a for a in self.values])

    def apply(self, func):
        return Vec([func(a) for a in self.values])



def _vec_func(func):
    def wrapper(arg):
        if isinstance(arg, Vec):
            return arg.apply(func)
        return func(arg)

    return wrapper


def _vec_min(*args):
    if len(args) == 1 and isinstance(args[0], Vec):
        return min(args[0].values)
    if any(isinstance(arg, Vec) for arg in args):
        raise ValueError("min() does not support multiple vectors")
    return min(*args)


def _vec_max(*args):
    if len(args) == 1 and isinstance(args[0], Vec):
        return max(args[0].values)
    if any(isinstance(arg, Vec) for arg in args):
        raise ValueError("max() does not support multiple vectors")
    return max(*args)


class PlotBackend:
    def __init__(
        self,
        datasets: list[Dataset],
        state: PlotState,
        legend_labels: list[str] | None,
    ) -> None:
        self.datasets = datasets
        self.state = state
        self.legend_labels = legend_labels
        self.visible: list[bool] = [True for _ in datasets]
        self.base_y_by_id: dict[int, list[float]] = {id(ds): ds.y[:] for ds in datasets}
        self.active_plugins: dict[str, dict[str, Any]] = {}

    def ensure_visibility_length(self) -> None:
        while len(self.visible) < len(self.datasets):
            self.visible.append(True)

    def set_dataset_visible(self, idx: int, visible: bool) -> None:
        self.ensure_visibility_length()
        if 0 <= idx < len(self.visible):
            self.visible[idx] = visible

    def rename_dataset(self, idx: int, name: str) -> None:
        if 0 <= idx < len(self.datasets):
            self.datasets[idx].name = name

    def legend_label_for(self, idx: int) -> str:
        ds = self.datasets[idx]
        if self.legend_labels and idx < len(self.legend_labels):
            return self.legend_labels[idx]
        return ds.name

    def plot_datasets(self, ax) -> None:
        handles = []
        labels = []
        self.ensure_visibility_length()
        for idx, ds in enumerate(self.datasets):
            if idx < len(self.visible) and not self.visible[idx]:
                continue
            label = self.legend_label_for(idx)
            marker_face = ds.marker_face_color if ds.marker_fill else "none"
            (handle,) = ax.plot(
                ds.x,
                ds.y,
                label=label,
                linewidth=ds.line_width,
                linestyle=ds.line_style,
                color=ds.line_color,
                marker=ds.marker,
                markersize=ds.marker_size,
                markerfacecolor=marker_face,
                markeredgecolor=ds.marker_edge_color,
            )
            if ds.dx is not None or ds.dy is not None:
                ax.errorbar(
                    ds.x,
                    ds.y,
                    xerr=ds.dx,
                    yerr=ds.dy,
                    fmt="none",
                    ecolor=ds.line_color,
                    elinewidth=max(1.0, ds.line_width * 0.75),
                    capsize=3.0,
                )
            handles.append(handle)
            labels.append(label)
        if handles:
            ax.legend(handles=handles, labels=labels)

    def available_plugins(self) -> list[tuple[str, str]]:
        return [(p.plugin_id, p.name) for p in PLUGIN_LIST]

    def get_plugin_config(self, plugin_id: str) -> dict[str, Any] | None:
        config = self.active_plugins.get(plugin_id)
        if config is None:
            return None
        return dict(config)

    def enable_plugin(self, plugin_id: str, **config: Any) -> None:
        plugin = PLUGIN_DEFINITIONS.get(plugin_id)
        if plugin is None:
            raise ValueError(f"Unknown plugin: {plugin_id}")
        merged = dict(plugin.default_config)
        merged.update(config)
        self.active_plugins[plugin_id] = merged

    def disable_plugin(self, plugin_id: str) -> None:
        self.active_plugins.pop(plugin_id, None)

    def render_plugins(self, ax) -> None:
        for plugin_id, config in self.active_plugins.items():
            plugin = PLUGIN_DEFINITIONS.get(plugin_id)
            if plugin is None:
                continue
            plugin.render(ax, config)

    def apply_axes_state(self, ax) -> None:
        state = self.state
        if state.title is not None:
            ax.set_title(state.title)
        if state.title_size is not None:
            ax.title.set_fontsize(state.title_size)
        if state.xlabel is not None:
            ax.set_xlabel(state.xlabel)
        if state.xlabel_size is not None:
            ax.xaxis.label.set_size(state.xlabel_size)
        if state.ylabel is not None:
            ax.set_ylabel(state.ylabel)
        if state.ylabel_size is not None:
            ax.yaxis.label.set_size(state.ylabel_size)
        if state.xtick_size is not None:
            ax.tick_params(axis="x", labelsize=state.xtick_size)
        if state.ytick_size is not None:
            ax.tick_params(axis="y", labelsize=state.ytick_size)
        if state.x_major_step:
            ax.xaxis.set_major_locator(ticker.MultipleLocator(state.x_major_step))
        if state.y_major_step:
            ax.yaxis.set_major_locator(ticker.MultipleLocator(state.y_major_step))
        if state.minor_ticks:
            if state.x_minor_step:
                ax.xaxis.set_minor_locator(ticker.MultipleLocator(state.x_minor_step))
            else:
                ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
            if state.y_minor_step:
                ax.yaxis.set_minor_locator(ticker.MultipleLocator(state.y_minor_step))
            else:
                ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
        else:
            ax.xaxis.set_minor_locator(ticker.NullLocator())
            ax.yaxis.set_minor_locator(ticker.NullLocator())
        if state.world is not None:
            xmin, xmax, ymin, ymax = state.world
            ax.set_xlim(xmin, xmax)
            ax.set_ylim(ymin, ymax)
        elif state.autoscale:
            ax.relim()
            ax.autoscale()

    def render(self, ax) -> None:
        ax.clear()
        self.plot_datasets(ax)
        self.apply_axes_state(ax)
        self.render_plugins(ax)

    @staticmethod
    def find_local_extrema(ds: Dataset) -> list[tuple[str, int, float, float]]:
        extrema: list[tuple[str, int, float, float]] = []
        if len(ds.y) < 3:
            return extrema
        for i in range(1, len(ds.y) - 1):
            y0 = ds.y[i - 1]
            y1 = ds.y[i]
            y2 = ds.y[i + 1]
            if y1 < y0 and y1 < y2:
                extrema.append(("min", i, ds.x[i], y1))
            elif y1 > y0 and y1 > y2:
                extrema.append(("max", i, ds.x[i], y1))
        return extrema

    def extrema_for_dataset(self, ds: Dataset) -> list[tuple[str, int, float, float]]:
        self.base_y_by_id.setdefault(id(ds), ds.y[:])
        extrema = self.find_local_extrema(ds)
        if not extrema and ds.y:
            ymin = min(range(len(ds.y)), key=lambda i: ds.y[i])
            ymax = max(range(len(ds.y)), key=lambda i: ds.y[i])
            extrema = [
                ("min", ymin, ds.x[ymin], ds.y[ymin]),
                ("max", ymax, ds.x[ymax], ds.y[ymax]),
            ]
        return extrema

    def align_extrema(self, selections: list[tuple[Dataset, tuple[str, int, float, float]]]) -> None:
        if not selections:
            return
        target_y = sum(sel[1][3] for sel in selections) / len(selections)
        for ds, entry in selections:
            _, idx, _, yval = entry
            if idx < 0 or idx >= len(ds.y):
                continue
            delta = target_y - yval
            base_y = self.base_y_by_id.get(id(ds), ds.y)
            ds.y = [y + delta for y in base_y]

    def set_dataset_appearance(
        self,
        idx: int,
        *,
        line_width: float,
        line_style: str,
        line_color: str,
        marker: str,
        marker_size: float,
        marker_face_color: str,
        marker_edge_color: str,
        marker_fill: bool,
    ) -> None:
        if not (0 <= idx < len(self.datasets)):
            return
        ds = self.datasets[idx]
        ds.line_width = line_width
        ds.line_style = line_style
        ds.line_color = line_color or ds.line_color
        ds.marker = marker
        ds.marker_size = marker_size
        ds.marker_face_color = marker_face_color or ds.marker_face_color
        ds.marker_edge_color = marker_edge_color or ds.marker_edge_color
        ds.marker_fill = marker_fill

    @staticmethod
    def safe_eval(expr: str, variables: dict[str, list[float]]) -> list[float]:
        vec_vars = {name: Vec(vals) for name, vals in variables.items()}
        allowed_names = {
            "abs": _vec_func(abs),
            "min": _vec_min,
            "max": _vec_max,
            "sqrt": _vec_func(math.sqrt),
            "log": _vec_func(math.log),
            "log10": _vec_func(math.log10),
            "exp": _vec_func(math.exp),
            "sin": _vec_func(math.sin),
            "cos": _vec_func(math.cos),
            "tan": _vec_func(math.tan),
            **vec_vars,
        }

        node = ast.parse(expr, mode="eval")
        for sub in ast.walk(node):
            if isinstance(sub, (ast.Import, ast.ImportFrom, ast.Attribute)):
                raise ValueError("Unsupported expression")
            if isinstance(sub, ast.Call):
                if not isinstance(sub.func, ast.Name):
                    raise ValueError("Unsupported function")
                if sub.func.id not in allowed_names:
                    raise ValueError("Unsupported function")
        code = compile(node, "<transform>", "eval")
        result = eval(code, {"__builtins__": {}}, allowed_names)
        if isinstance(result, Vec):
            return result.values
        if isinstance(result, (int, float)):
            n = len(next(iter(variables.values())))
            return [float(result) for _ in range(n)]
        raise ValueError("Expression did not evaluate to a vector")

    def apply_transform(self, text: str) -> int:
        if "=" not in text:
            raise ValueError("Missing '='")
        lhs, rhs = [part.strip() for part in text.split("=", 1)]
        if len(lhs) < 2 or lhs[0] not in {"x", "y"}:
            raise ValueError("Left side must be xN or yN")
        target_axis = lhs[0]
        try:
            target_index = int(lhs[1:])
        except ValueError as exc:
            raise ValueError("Left side index must be an integer") from exc

        variables: dict[str, list[float]] = {}
        for idx, ds in enumerate(self.datasets):
            variables[f"x{idx}"] = ds.x
            variables[f"y{idx}"] = ds.y
        if not variables:
            raise ValueError("No datasets loaded")

        result = self.safe_eval(rhs, variables)
        if target_index < 0:
            raise ValueError("Index must be >= 0")

        created = False
        if target_index < len(self.datasets):
            target = self.datasets[target_index]
        else:
            base = self.datasets[0]
            target = Dataset(name=f"set{target_index}", x=base.x[:], y=base.y[:])
            self.datasets.append(target)
            created = True

        if target_axis == "x":
            if len(result) != len(target.x):
                raise ValueError("Result length does not match target x length")
            target.x = result
        else:
            if len(result) != len(target.y):
                raise ValueError("Result length does not match target y length")
            target.y = result

        self.base_y_by_id[id(target)] = target.y[:]
        if created:
            self.visible.append(True)
        return target_index



def render_hardcopy(
    datasets: list[Dataset],
    output_path: Path,
    title: str | None,
    xlabel: str | None,
    ylabel: str | None,
    world: list[float] | None,
    autoscale: bool,
    legend_labels: list[str] | None,
) -> None:
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    backend = PlotBackend(
        datasets=datasets,
        state=PlotState(
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            world=world,
            autoscale=autoscale,
        ),
        legend_labels=legend_labels,
    )
    backend.plot_datasets(ax)
    backend.apply_axes_state(ax)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
