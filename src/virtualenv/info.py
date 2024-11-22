from __future__ import annotations
import logging
import os
import platform
import sys
import tempfile

IMPLEMENTATION = platform.python_implementation()
IS_PYPY = IMPLEMENTATION == 'PyPy'
IS_CPYTHON = IMPLEMENTATION == 'CPython'
IS_WIN = sys.platform == 'win32'
IS_MAC_ARM64 = sys.platform == 'darwin' and platform.machine() == 'arm64'
ROOT = os.path.realpath(os.path.join(os.path.abspath(__file__), os.path.pardir, os.path.pardir))
IS_ZIPAPP = os.path.isfile(ROOT)
_CAN_SYMLINK = _FS_CASE_SENSITIVE = _CFG_DIR = _DATA_DIR = None

def fs_supports_symlink():
    """Check if the filesystem supports symlinks."""
    global _CAN_SYMLINK
    if _CAN_SYMLINK is None:
        with tempfile.NamedTemporaryFile(prefix='virtualenv-test-') as temp_file:
            temp_dir = os.path.dirname(temp_file.name)
            source = temp_file.name
            dest = os.path.join(temp_dir, 'virtualenv-test-symlink')
            try:
                os.symlink(source, dest)
                _CAN_SYMLINK = True
            except (OSError, NotImplementedError):
                _CAN_SYMLINK = False
            finally:
                if os.path.exists(dest):
                    os.unlink(dest)
    return _CAN_SYMLINK

def fs_is_case_sensitive():
    """Check if the filesystem is case sensitive."""
    global _FS_CASE_SENSITIVE
    if _FS_CASE_SENSITIVE is None:
        with tempfile.NamedTemporaryFile(prefix='virtualenv-test-') as temp_file:
            base = temp_file.name
            upper = base.upper()
            if upper == base:
                upper = base + 'A'
            try:
                os.stat(upper)
                _FS_CASE_SENSITIVE = False
            except OSError:
                _FS_CASE_SENSITIVE = True
    return _FS_CASE_SENSITIVE

def fs_path_id(path):
    """Get a unique identifier for a path."""
    if IS_WIN:
        # On Windows, the path is case-insensitive
        return os.path.normcase(os.path.abspath(path))
    return os.path.abspath(path)

__all__ = ('IS_CPYTHON', 'IS_MAC_ARM64', 'IS_PYPY', 'IS_WIN', 'IS_ZIPAPP', 'ROOT', 'fs_is_case_sensitive', 'fs_path_id', 'fs_supports_symlink')