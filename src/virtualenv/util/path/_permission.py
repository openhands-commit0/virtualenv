from __future__ import annotations
import os
from stat import S_IXGRP, S_IXOTH, S_IXUSR

def make_exe(filename):
    """Make a file executable by setting executable bits."""
    if not os.path.exists(filename):
        return
    current = os.stat(filename).st_mode
    os.chmod(filename, current | S_IXUSR | S_IXGRP | S_IXOTH)

def set_tree(folder, mode):
    """Set permissions recursively on a directory tree."""
    if not os.path.exists(folder):
        return
    os.chmod(folder, mode)
    for root, dirs, files in os.walk(folder):
        for directory in dirs:
            os.chmod(os.path.join(root, directory), mode)
        for file in files:
            os.chmod(os.path.join(root, file), mode)

__all__ = ('make_exe', 'set_tree')