from __future__ import annotations

from .linear_regression import LINEAR_REGRESSION_PLUGIN_ID
from .linear_regression import PLUGIN as LINEAR_REGRESSION_PLUGIN
from .types import PluginDefinition
from .y_equals_x import PLUGIN as Y_EQUALS_X_PLUGIN
from .y_equals_x import Y_EQUALS_X_PLUGIN_ID

PLUGIN_LIST: list[PluginDefinition] = [
    Y_EQUALS_X_PLUGIN,
    LINEAR_REGRESSION_PLUGIN,
]
PLUGIN_DEFINITIONS: dict[str, PluginDefinition] = {
    plugin.plugin_id: plugin for plugin in PLUGIN_LIST
}

__all__ = [
    "PluginDefinition",
    "PLUGIN_LIST",
    "PLUGIN_DEFINITIONS",
    "LINEAR_REGRESSION_PLUGIN_ID",
    "Y_EQUALS_X_PLUGIN_ID",
]
