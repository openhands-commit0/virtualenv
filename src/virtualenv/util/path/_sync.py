from __future__ import annotations
import logging
import os
import shutil
import sys
from stat import S_IWUSR

class _Debug:

    def __init__(self, src, dest) -> None:
        self.src = src
        self.dest = dest

    def __str__(self) -> str:
        return f'{"directory " if self.src.is_dir() else ""}{self.src!s} to {self.dest!s}'
__all__ = ['copy', 'copytree', 'ensure_dir', 'safe_delete', 'symlink', 'symlink']