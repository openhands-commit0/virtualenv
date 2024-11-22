from __future__ import annotations
from .base import PluginLoader

class Discovery(PluginLoader):
    """Discovery plugins."""

    def __init__(self) -> None:
        super().__init__('virtualenv.discovery')

def get_discover(parser, args):
    """Get the discovery plugin."""
    discover = Discovery()
    discover.load()
    return discover.select(parser, args)

__all__ = ['Discovery', 'get_discover']