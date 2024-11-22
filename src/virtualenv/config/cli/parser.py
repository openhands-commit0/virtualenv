from __future__ import annotations
import os
from argparse import SUPPRESS, ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from collections import OrderedDict
from virtualenv.config.convert import get_type
from virtualenv.config.env_var import get_env_var
from virtualenv.config.ini import IniConfig

class VirtualEnvOptions(Namespace):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._src = None
        self._sources = {}

    def __setattr__(self, key, value) -> None:
        if getattr(self, '_src', None) is not None:
            self._sources[key] = self._src
        super().__setattr__(key, value)

    def __repr__(self) -> str:
        items = [f'{k}={v}' for k, v in vars(self).items() if not k.startswith('_')]
        return f'{type(self).__name__}({", ".join(items)})'

class VirtualEnvConfigParser(ArgumentParser):
    """Custom option parser which updates its defaults by checking the configuration files and environmental vars."""

    def __init__(self, options=None, env=None, *args, **kwargs) -> None:
        env = os.environ if env is None else env
        self.file_config = IniConfig(env)
        self.epilog_list = []
        self.env = env
        kwargs['epilog'] = self.file_config.epilog
        kwargs['add_help'] = False
        kwargs['formatter_class'] = HelpFormatter
        kwargs['prog'] = 'virtualenv'
        super().__init__(*args, **kwargs)
        self._fixed = set()
        if options is not None and (not isinstance(options, VirtualEnvOptions)):
            msg = 'options must be of type VirtualEnvOptions'
            raise TypeError(msg)
        self.options = VirtualEnvOptions() if options is None else options
        self._interpreter = None
        self._app_data = None

class HelpFormatter(ArgumentDefaultsHelpFormatter):

    def __init__(self, prog) -> None:
        super().__init__(prog, max_help_position=32, width=240)
__all__ = ['HelpFormatter', 'VirtualEnvConfigParser', 'VirtualEnvOptions']