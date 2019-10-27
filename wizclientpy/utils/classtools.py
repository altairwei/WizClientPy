"""This module contains a series of tools to help construct classes."""

from wizclientpy.errors import PrivateError


class Privacy:
    """Limits the access to private attribute."""
    pass


class MetaSingleton(type):
    """Meta class of all singleton"""

    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super().__call__(*args, **kwargs)
        return cls.__instances[cls]
