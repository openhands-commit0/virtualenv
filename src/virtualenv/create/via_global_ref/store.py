from __future__ import annotations
import os
from pathlib import Path

def is_store_python(interpreter):
    """Check if the interpreter is a Windows Store Python."""
    if not interpreter.platform == 'win32':
        return False
    return str(interpreter.executable).startswith(os.path.expandvars('%LOCALAPPDATA%\\Microsoft\\WindowsApps'))

def handle_store_python(interpreter):
    """Handle Windows Store Python by finding the actual Python executable."""
    if not is_store_python(interpreter):
        return interpreter
    # Windows Store Python is a proxy, find the actual Python executable
    for path in os.environ.get('PATH', '').split(os.pathsep):
        python_path = os.path.join(path, 'python.exe')
        if os.path.exists(python_path) and not is_store_python(python_path):
            return python_path
    return interpreter

__all__ = ['handle_store_python', 'is_store_python']