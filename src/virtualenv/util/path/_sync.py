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

def ensure_dir(path):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)

def safe_delete(path):
    """Delete a file or directory safely."""
    if not os.path.exists(path):
        return
    if os.path.isfile(path) or os.path.islink(path):
        try:
            os.unlink(path)
        except OSError:
            os.chmod(path, S_IWUSR)
            os.unlink(path)
    else:
        shutil.rmtree(path)

def copy(src, dest):
    """Copy a file from src to dest."""
    if os.path.islink(src):
        if os.path.exists(dest):
            os.unlink(dest)
        os.symlink(os.readlink(src), dest)
    else:
        shutil.copy2(src, dest)

def copytree(src, dest):
    """Copy a directory tree from src to dest."""
    if not os.path.exists(dest):
        os.makedirs(dest)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dest, item)
        if os.path.isdir(s):
            copytree(s, d)
        else:
            copy(s, d)

def symlink(src, dest):
    """Create a symbolic link pointing to src named dest."""
    if os.path.exists(dest):
        os.unlink(dest)
    os.symlink(src, dest)

__all__ = ['copy', 'copytree', 'ensure_dir', 'safe_delete', 'symlink']