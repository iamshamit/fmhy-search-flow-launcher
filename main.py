import sys
import os

_plugin_root = os.path.abspath(os.path.dirname(__file__))
sys.path.append(_plugin_root)
sys.path.append(os.path.join(_plugin_root, "lib"))

from src.plugin import FMHYSearch

if __name__ == "__main__":
    FMHYSearch()
