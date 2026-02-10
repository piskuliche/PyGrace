from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class PluginDefinition:
    plugin_id: str
    name: str
    default_config: dict[str, Any]
    render: Callable[[Any, dict[str, Any]], None]
