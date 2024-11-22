from __future__ import annotations
from operator import attrgetter
from zipfile import ZipFile

class Wheel:
    def __init__(self, path) -> None:
        self.path = path
        self._parts = path.stem.split('-')

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.path})'

    def __str__(self) -> str:
        return str(self.path)

    @property
    def name(self):
        """Get the name of the wheel."""
        return self._parts[0]

    @property
    def version(self):
        """Get the version of the wheel."""
        return self._parts[1]

    @property
    def filename(self):
        """Get the filename of the wheel."""
        return self.path.name

    @classmethod
    def from_path(cls, path):
        """Create a wheel from a path."""
        return cls(path)

def discover_wheels(folder, distribution):
    """Discover wheels in a folder."""
    wheels = []
    for path in folder.iterdir():
        if path.suffix == '.whl':
            wheel = Wheel(path)
            if wheel.name == distribution:
                wheels.append(wheel)
    return sorted(wheels, key=attrgetter('version'), reverse=True)

class Version:
    bundle = 'bundle'
    embed = 'embed'
    non_version = (bundle, embed)

__all__ = ['Version', 'Wheel', 'discover_wheels']