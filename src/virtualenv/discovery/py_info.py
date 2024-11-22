"""
The PythonInfo contains information about a concrete instance of a Python interpreter.

Note: this file is also used to query target interpreters, so can only use standard library methods
"""
from __future__ import annotations
import json
import logging
import os
import platform
import re
import sys
import sysconfig
import warnings
from collections import OrderedDict, namedtuple
from string import digits

def _get_path_extensions():
    """Get the executable path extensions from the PATHEXT environment variable."""
    if sys.platform == 'win32':
        exts = os.environ.get('PATHEXT', '').split(os.pathsep)
        return [i.lower() for i in exts], {i.lower() for i in exts}
    return [], set()

VersionInfo = namedtuple('VersionInfo', ['major', 'minor', 'micro', 'releaselevel', 'serial'])
EXTENSIONS = _get_path_extensions()
_CONF_VAR_RE = re.compile('\\{\\w+\\}')

class PythonInfo:
    """Contains information for a Python interpreter."""

    def __init__(self) -> None:

        def abs_path(v):
            return None if v is None else os.path.abspath(v)
        self.platform = sys.platform
        self.implementation = platform.python_implementation()
        if self.implementation == 'PyPy':
            self.pypy_version_info = tuple(sys.pypy_version_info)
        self.version_info = VersionInfo(*sys.version_info)
        self.architecture = 64 if sys.maxsize > 2 ** 32 else 32
        self.version_nodot = sysconfig.get_config_var('py_version_nodot')
        self.version = sys.version
        self.os = os.name
        self.prefix = abs_path(getattr(sys, 'prefix', None))
        self.base_prefix = abs_path(getattr(sys, 'base_prefix', None))
        self.real_prefix = abs_path(getattr(sys, 'real_prefix', None))
        self.base_exec_prefix = abs_path(getattr(sys, 'base_exec_prefix', None))
        self.exec_prefix = abs_path(getattr(sys, 'exec_prefix', None))
        self.executable = abs_path(sys.executable)
        self.original_executable = abs_path(self.executable)
        self.system_executable = self._fast_get_system_executable()
        try:
            __import__('venv')
            has = True
        except ImportError:
            has = False
        self.has_venv = has
        self.path = sys.path
        self.file_system_encoding = sys.getfilesystemencoding()
        self.stdout_encoding = getattr(sys.stdout, 'encoding', None)
        scheme_names = sysconfig.get_scheme_names()
        if 'venv' in scheme_names:
            self.sysconfig_scheme = 'venv'
            self.sysconfig_paths = {i: sysconfig.get_path(i, expand=False, scheme=self.sysconfig_scheme) for i in sysconfig.get_path_names()}
            self.distutils_install = {}
        elif sys.version_info[:2] == (3, 10) and 'deb_system' in scheme_names:
            self.sysconfig_scheme = 'posix_prefix'
            self.sysconfig_paths = {i: sysconfig.get_path(i, expand=False, scheme=self.sysconfig_scheme) for i in sysconfig.get_path_names()}
            self.distutils_install = {}
        else:
            self.sysconfig_scheme = None
            self.sysconfig_paths = {i: sysconfig.get_path(i, expand=False) for i in sysconfig.get_path_names()}
            self.distutils_install = self._distutils_install().copy()
        makefile = getattr(sysconfig, 'get_makefile_filename', getattr(sysconfig, '_get_makefile_filename', None))
        self.sysconfig = {k: v for k, v in [('makefile_filename', makefile())] if k is not None}
        config_var_keys = set()
        for element in self.sysconfig_paths.values():
            config_var_keys.update((k[1:-1] for k in _CONF_VAR_RE.findall(element)))
        config_var_keys.add('PYTHONFRAMEWORK')
        self.sysconfig_vars = {i: sysconfig.get_config_var(i or '') for i in config_var_keys}
        confs = {k: self.system_prefix if v is not None and v.startswith(self.prefix) else v for k, v in self.sysconfig_vars.items()}
        self.system_stdlib = self.sysconfig_path('stdlib', confs)
        self.system_stdlib_platform = self.sysconfig_path('platstdlib', confs)
        self.max_size = getattr(sys, 'maxsize', getattr(sys, 'maxint', None))
        self._creators = None

    def _fast_get_system_executable(self):
        """Try to get the system executable by just looking at properties."""
        if self.base_prefix is None and self.base_exec_prefix is None:
            return self.executable
        if self.real_prefix is not None:
            return self.executable
        if self.prefix != self.base_prefix and self.base_prefix is not None:
            return None
        if self.exec_prefix != self.base_exec_prefix and self.base_exec_prefix is not None:
            return None
        return self.executable

    def __repr__(self) -> str:
        return '{}({!r})'.format(self.__class__.__name__, {k: v for k, v in self.__dict__.items() if not k.startswith('_')})

    def __str__(self) -> str:
        return '{}({})'.format(self.__class__.__name__, ', '.join((f'{k}={v}' for k, v in (('spec', self.spec), ('system' if self.system_executable is not None and self.system_executable != self.executable else None, self.system_executable), ('original' if self.original_executable not in {self.system_executable, self.executable} else None, self.original_executable), ('exe', self.executable), ('platform', self.platform), ('version', repr(self.version)), ('encoding_fs_io', f'{self.file_system_encoding}-{self.stdout_encoding}')) if k is not None)))

    def satisfies(self, spec, impl_must_match):
        """Check if a given specification can be satisfied by the this python interpreter instance."""
        if spec.implementation is not None and impl_must_match and spec.implementation != self.implementation:
            return False
        if spec.architecture is not None and spec.architecture != self.architecture:
            return False
        for our, req in zip(self.version_info[0:3], (spec.major, spec.minor, spec.micro)):
            if req is not None and our is not None and our != req:
                return False
        return True

    _current_system = None
    _current = None

    @classmethod
    def current(cls, app_data=None):
        """
        This locates the current host interpreter information. This might be different than what we run into in case
        the host python has been upgraded from underneath us.
        """
        if cls._current is None:
            cls._current = cls()
        return cls._current

    @classmethod
    def current_system(cls, app_data=None) -> PythonInfo:
        """
        This locates the current host interpreter information. This might be different than what we run into in case
        the host python has been upgraded from underneath us.
        """
        if cls._current_system is None:
            cls._current_system = cls.from_exe(sys.executable, app_data=app_data)
        return cls._current_system

    @classmethod
    def from_exe(cls, exe, app_data=None, raise_on_error=True, ignore_cache=False, resolve_to_host=True, env=None):
        """Given a path to an executable get the python information."""
        # First, check if we have this information cached
        if not ignore_cache and exe in cls._cache_exe_discovery:
            result = cls._cache_exe_discovery[exe]
            if result is not None or not raise_on_error:
                return result
            msg = f'failed to get interpreter info for {exe}'
            raise RuntimeError(msg)

        # If not cached, create a new instance and cache it
        try:
            info = cls()
            info.executable = exe
            cls._cache_exe_discovery[exe] = info
            return info
        except Exception as exception:
            cls._cache_exe_discovery[exe] = None
            if raise_on_error:
                raise
            logging.error('failed to get interpreter info for %s because %r', exe, exception)
            return None
    _cache_exe_discovery = {}
if __name__ == '__main__':
    argv = sys.argv[1:]
    if len(argv) >= 1:
        start_cookie = argv[0]
        argv = argv[1:]
    else:
        start_cookie = ''
    if len(argv) >= 1:
        end_cookie = argv[0]
        argv = argv[1:]
    else:
        end_cookie = ''
    sys.argv = sys.argv[:1] + argv
    info = PythonInfo()._to_json()
    sys.stdout.write(''.join((start_cookie[::-1], info, end_cookie[::-1])))