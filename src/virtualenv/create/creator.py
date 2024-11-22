from __future__ import annotations
import json
import logging
import os
import sys
from abc import ABC, abstractmethod
from argparse import ArgumentTypeError
from ast import literal_eval
from collections import OrderedDict
from pathlib import Path
from virtualenv.discovery.cached_py_info import LogCmd
from virtualenv.util.path import safe_delete
from virtualenv.util.subprocess import run_cmd
from virtualenv.version import __version__
from .pyenv_cfg import PyEnvCfg
HERE = Path(os.path.abspath(__file__)).parent
DEBUG_SCRIPT = HERE / 'debug.py'

class CreatorMeta:

    def __init__(self) -> None:
        self.error = None

class Creator(ABC):
    """A class that given a python Interpreter creates a virtual environment."""

    def __init__(self, options, interpreter) -> None:
        """
        Construct a new virtual environment creator.

        :param options: the CLI option as parsed from :meth:`add_parser_arguments`
        :param interpreter: the interpreter to create virtual environment from
        """
        self.interpreter = interpreter
        self._debug = None
        self.dest = Path(options.dest)
        self.clear = options.clear
        self.no_vcs_ignore = options.no_vcs_ignore
        self.pyenv_cfg = PyEnvCfg.from_folder(self.dest)
        self.app_data = options.app_data
        self.env = options.env

    def _args(self):
        return [
            ('dest', self.dest),
            ('clear', self.clear),
            ('no_vcs_ignore', self.no_vcs_ignore),
            ('interpreter', self.interpreter),
        ]

    def __repr__(self) -> str:
        items = [f'{k}={v}' for k, v in self._args()]
        return f'{self.__class__.__name__}({", ".join(items)})'

    @classmethod
    def can_create(cls, interpreter):
        """
        Determine if we can create a virtual environment.

        :param interpreter: the interpreter in question
        :return: ``None`` if we can't create, any other object otherwise that will be forwarded to :meth:`add_parser_arguments`
        """
        return CreatorMeta()

    @classmethod
    def add_parser_arguments(cls, parser, interpreter, meta, app_data):
        """
        Add CLI arguments for the creator.

        :param parser: the CLI parser
        :param app_data: the application data folder
        :param interpreter: the interpreter we're asked to create virtual environment for
        :param meta: value as returned by :meth:`can_create`
        """
        parser.add_argument(
            '--clear',
            dest='clear',
            action='store_true',
            help='remove the destination directory if exist',
            default=False,
        )
        parser.add_argument(
            '--no-vcs-ignore',
            dest='no_vcs_ignore',
            action='store_true',
            help='don\'t create VCS ignore directive in the destination directory',
            default=False,
        )

    @abstractmethod
    def create(self):
        """Perform the virtual environment creation."""
        if self.dest.exists() and self.clear:
            safe_delete(self.dest)
        self.dest.mkdir(parents=True, exist_ok=True)
        if not self.no_vcs_ignore:
            self.setup_ignore_vcs()

    @classmethod
    def validate_dest(cls, raw_value):
        """No path separator in the path, valid chars and must be write-able."""
        if not raw_value:
            msg = 'destination directory cannot be empty'
            raise ArgumentTypeError(msg)
        try:
            value = Path(raw_value)
            if value.exists() and not value.is_dir():
                msg = f'cannot create directory {value} - file exists'
                raise ArgumentTypeError(msg)
            return value
        except Exception as exception:
            msg = f'invalid destination directory {raw_value} - {exception}'
            raise ArgumentTypeError(msg)

    def setup_ignore_vcs(self):
        """Generate ignore instructions for version control systems."""
        if self.no_vcs_ignore:
            return
        for ignore_file, content in [
            ('.gitignore', '# created by virtualenv automatically\n*\n'),
            ('.hgignore', 'syntax:glob\n# created by virtualenv automatically\n*\n'),
        ]:
            path = self.dest / ignore_file
            if not path.exists():
                path.write_text(content, encoding='utf-8')

    @property
    def debug(self):
        """:return: debug information about the virtual environment (only valid after :meth:`create` has run)"""
        if self._debug is None:
            self._debug = {}
            # Run debug.py in the virtual environment to collect debug info
            cmd = [str(self.dest / 'bin' / 'python'), str(DEBUG_SCRIPT)]
            result = run_cmd(cmd)
            if result.returncode == 0:
                self._debug = json.loads(result.out)
        return self._debug
def get_env_debug_info(env):
    """Get debug information about the environment."""
    debug_info = {}
    for key, value in env.items():
        if key.startswith('VIRTUALENV_'):
            debug_info[key] = value
    return debug_info

__all__ = ['Creator', 'CreatorMeta', 'get_env_debug_info']