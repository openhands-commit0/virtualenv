from __future__ import annotations
import logging
import os
from typing import ClassVar

class TypeData:

    def __init__(self, default_type, as_type) -> None:
        self.default_type = default_type
        self.as_type = as_type

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(base={self.default_type}, as={self.as_type})'

class BoolType(TypeData):
    BOOLEAN_STATES: ClassVar[dict[str, bool]] = {'1': True, 'yes': True, 'true': True, 'on': True, '0': False, 'no': False, 'false': False, 'off': False}

class NoneType(TypeData):
    pass

class ListType(TypeData):

    def _validate(self):
        """no op."""
        pass

    def split_values(self, value):
        """
        Split the provided value into a list.

        First this is done by newlines. If there were no newlines in the text,
        then we next try to split by comma.
        """
        if not value:
            return []
        values = [i.strip() for i in value.splitlines() if i.strip()]
        if not values:
            values = [i.strip() for i in value.split(',') if i.strip()]
        return values

def convert(value, as_type, source):
    """Convert the value as a given type where the value comes from the given source."""
    if value is None or isinstance(value, as_type):
        return value
    try:
        if as_type == bool:
            if isinstance(value, str):
                value = value.lower()
                if value not in BoolType.BOOLEAN_STATES:
                    msg = f'invalid truth value {value!r}'
                    raise ValueError(msg)
                return BoolType.BOOLEAN_STATES[value]
            return bool(value)
        if as_type == list:
            if isinstance(value, str):
                value = ListType(list, as_type).split_values(value)
            return list(value)
        if as_type == type(None):
            return None
        return as_type(value)
    except Exception as exception:
        logging.error('failed to convert %r to %r from %r because %r', value, as_type, source, exception)
        raise

def get_type(value):
    """Get type information for a value."""
    as_type = type(value)
    for key, class_type in _CONVERT.items():
        if as_type is key:
            return class_type(as_type, as_type)
    return TypeData(as_type, as_type)

_CONVERT = {bool: BoolType, type(None): NoneType, list: ListType}
__all__ = ['convert', 'get_type']