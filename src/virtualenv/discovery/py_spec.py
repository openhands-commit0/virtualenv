"""A Python specification is an abstract requirement definition of an interpreter."""
from __future__ import annotations
import os
import re
PATTERN = re.compile('^(?P<impl>[a-zA-Z]+)?(?P<version>[0-9.]+)?(?:-(?P<arch>32|64))?$')

class PythonSpec:
    """Contains specification about a Python Interpreter."""

    def __init__(self, str_spec: str, implementation: str | None, major: int | None, minor: int | None, micro: int | None, architecture: int | None, path: str | None) -> None:
        self.str_spec = str_spec
        self.implementation = implementation
        self.major = major
        self.minor = minor
        self.micro = micro
        self.architecture = architecture
        self.path = path

    def generate_re(self, *, windows: bool) -> re.Pattern:
        """Generate a regular expression for matching against a filename."""
        pass

    def satisfies(self, spec):
        """Called when there's a candidate metadata spec to see if compatible - e.g. PEP-514 on Windows."""
        pass

    def __repr__(self) -> str:
        name = type(self).__name__
        params = ('implementation', 'major', 'minor', 'micro', 'architecture', 'path')
        items = [f'{k}={getattr(self, k)}' for k in params if getattr(self, k) is not None]
        return f'{name}({", ".join(items)})'
__all__ = ['PythonSpec']