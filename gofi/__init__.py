from .config import Config
from .gofi import Gofi

__version__ = "0.9.9"
VERSION = tuple(map(int, __version__.split(".")))

__all__ = ["Gofi", "Config"]
