from __future__ import annotations

from .types import PluginDefinition

LINEAR_REGRESSION_PLUGIN_ID = "linear_regression"


def _render_linear_regression(ax, config: dict[str, object], backend: object) -> None:
    # Typed loosely to keep plugin package decoupled from backend module imports.
    datasets = getattr(backend, "datasets", [])
    if not datasets:
        return

    idx = int(config.get("dataset_index", 0))
    if idx < 0 or idx >= len(datasets):
        return

    ds = datasets[idx]
    if len(ds.x) < 2 or len(ds.y) < 2:
        return

    n = len(ds.x)
    x_mean = sum(ds.x) / n
    y_mean = sum(ds.y) / n
    sxx = sum((x - x_mean) ** 2 for x in ds.x)
    if sxx == 0:
        return
    sxy = sum((x - x_mean) * (y - y_mean) for x, y in zip(ds.x, ds.y))

    slope = sxy / sxx
    intercept = y_mean - slope * x_mean

    xmin = min(ds.x)
    xmax = max(ds.x)
    xs = [xmin, xmax]
    ys = [slope * xmin + intercept, slope * xmax + intercept]

    color = str(config.get("color", "tab:green"))
    linewidth = float(config.get("line_width", 2.0))
    linestyle = str(config.get("line_style", "-"))
    ax.plot(xs, ys, color=color, linewidth=linewidth, linestyle=linestyle, zorder=4)


PLUGIN = PluginDefinition(
    plugin_id=LINEAR_REGRESSION_PLUGIN_ID,
    name="Linear Regression...",
    default_config={
        "enabled": False,
        "dataset_index": 0,
        "color": "tab:green",
        "line_width": 2.0,
        "line_style": "-",
    },
    render=_render_linear_regression,
)
