from __future__ import annotations
from abc import ABC
from pathlib import Path
from virtualenv.seed.seeder import Seeder
from virtualenv.seed.wheels import Version
PERIODIC_UPDATE_ON_BY_DEFAULT = True

class BaseEmbed(Seeder, ABC):

    def __init__(self, options) -> None:
        super().__init__(options, enabled=options.no_seed is False)
        self.download = options.download
        self.extra_search_dir = [i.resolve() for i in options.extra_search_dir if i.exists()]
        self.pip_version = options.pip
        self.setuptools_version = options.setuptools
        self.wheel_version = options.wheel
        self.no_pip = options.no_pip
        self.no_setuptools = options.no_setuptools
        self.no_wheel = options.no_wheel
        self.app_data = options.app_data
        self.periodic_update = not options.no_periodic_update
        if not self.distribution_to_versions():
            self.enabled = False

    def __repr__(self) -> str:
        result = self.__class__.__name__
        result += '('
        if self.extra_search_dir:
            result += f'extra_search_dir={", ".join(str(i) for i in self.extra_search_dir)},'
        result += f'download={self.download},'
        for distribution in self.distributions():
            if getattr(self, f'no_{distribution}'):
                continue
            version = getattr(self, f'{distribution}_version', None)
            if version == 'none':
                continue
            ver = f'={version or 'latest'}'
            result += f' {distribution}{ver},'
        return result[:-1] + ')'
__all__ = ['BaseEmbed']