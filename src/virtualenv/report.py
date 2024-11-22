from __future__ import annotations
import logging
import sys

LEVELS = {0: logging.CRITICAL, 1: logging.ERROR, 2: logging.WARNING, 3: logging.INFO, 4: logging.DEBUG, 5: logging.NOTSET}
MAX_LEVEL = max(LEVELS.keys())
LOGGER = logging.getLogger()

def setup_report(verbosity, show_pid=False):
    """Setup logging based on verbosity level."""
    level = LEVELS.get(min(verbosity, MAX_LEVEL), logging.CRITICAL)
    LOGGER.setLevel(level)
    if not LOGGER.handlers:
        handler = logging.StreamHandler(stream=sys.stderr)
        if show_pid:
            formatter = logging.Formatter('%(asctime)s %(process)d %(levelname)s %(message)s')
        else:
            formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        LOGGER.addHandler(handler)
    return LOGGER

__all__ = ['LEVELS', 'MAX_LEVEL', 'setup_report']