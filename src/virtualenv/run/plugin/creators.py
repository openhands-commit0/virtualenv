from __future__ import annotations
from collections import OrderedDict, defaultdict
from typing import TYPE_CHECKING, NamedTuple
from virtualenv.create.describe import Describe
from virtualenv.create.via_global_ref.builtin.builtin_way import VirtualenvBuiltin
from .base import ComponentBuilder
if TYPE_CHECKING:
    from virtualenv.create.creator import Creator, CreatorMeta

class CreatorInfo(NamedTuple):
    key_to_class: dict[str, type[Creator]]
    key_to_meta: dict[str, CreatorMeta]
    describe: type[Describe] | None
    builtin_key: str

class CreatorSelector(ComponentBuilder):

    def __init__(self, interpreter, parser) -> None:
        creators, self.key_to_meta, self.describe, self.builtin_key = self.for_interpreter(interpreter)
        super().__init__(interpreter, parser, 'creator', creators)

    @staticmethod
    def for_interpreter(interpreter):
        """Find the available creators for the interpreter."""
        key_to_class = OrderedDict()
        key_to_meta = defaultdict(list)
        describe = None
        builtin_key = None

        for key, creator_class in ComponentBuilder.options('virtualenv.create').items():
            if key == 'builtin':
                continue
            meta = creator_class.can_create(interpreter)
            if meta is not None:
                if meta.error is None:
                    if issubclass(creator_class, VirtualenvBuiltin):
                        builtin_key = key
                    key_to_class[key] = creator_class
                key_to_meta[key].append(meta)

        if not key_to_class and builtin_key:
            key_to_class[builtin_key] = VirtualenvBuiltin
            key_to_meta[builtin_key] = []

        return CreatorInfo(key_to_class, key_to_meta, describe, builtin_key)

__all__ = ['CreatorInfo', 'CreatorSelector']