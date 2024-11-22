from __future__ import annotations
import re
import sys
from abc import ABC
from collections import OrderedDict
from pathlib import Path
from virtualenv.create.describe import PosixSupports, WindowsSupports
from virtualenv.create.via_global_ref.builtin.ref import RefMust, RefWhen
from virtualenv.create.via_global_ref.builtin.via_global_self_do import ViaGlobalRefVirtualenvBuiltin

class CPython(ViaGlobalRefVirtualenvBuiltin, ABC):
    pass

class CPythonPosix(CPython, PosixSupports, ABC):
    """Create a CPython virtual environment on POSIX platforms."""

class CPythonWindows(CPython, WindowsSupports, ABC):
    pass
_BREW = re.compile('/(usr/local|opt/homebrew)/(opt/python@3\\.\\d{1,2}|Cellar/python@3\\.\\d{1,2}/3\\.\\d{1,2}\\.\\d{1,2})/Frameworks/Python\\.framework/Versions/3\\.\\d{1,2}')

def is_mac_os_framework(interpreter):
    """Check if the interpreter is a macOS framework build."""
    return sys.platform == 'darwin' and interpreter.real_prefix is None and interpreter.base_prefix is not None

def is_macos_brew(interpreter):
    """Check if the interpreter is a Homebrew-installed Python on macOS."""
    if not sys.platform == 'darwin':
        return False
    return bool(_BREW.search(str(interpreter.executable)))

__all__ = ['CPython', 'CPythonPosix', 'CPythonWindows', 'is_mac_os_framework', 'is_macos_brew']