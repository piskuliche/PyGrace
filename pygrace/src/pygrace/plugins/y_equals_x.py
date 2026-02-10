from __future__ import annotations

from .types import PluginDefinition

Y_EQUALS_X_PLUGIN_ID = "y_equals_x_shaded"


def _render_y_equals_x_shaded(ax, config: dict[str, object], _backend: object) -> None:
    alpha_raw = config.get("alpha", 0.15)
    alpha = float(alpha_raw)
    alpha = max(0.0, min(1.0, alpha))

    x0, x1 = ax.get_xlim()
    xs = [x0, x1]
    ys = [x0, x1]

    ax.plot(xs, ys, linestyle="--", linewidth=1.5, color="dimgray", zorder=3)
    ax.fill_between(xs, [y - 1 for y in ys], [y + 1 for y in ys], color="dimgray", alpha=alpha, zorder=2)


PLUGIN = PluginDefinition(
    plugin_id=Y_EQUALS_X_PLUGIN_ID,
    name="y = x...",
    default_config={"alpha": 0.15, "enabled": False},
    render=_render_y_equals_x_shaded,
)
