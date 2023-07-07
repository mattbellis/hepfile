"""
A file description modeled after the ROOT analysis toolkit and common use-cases
in High Energy Physics. Implemented in HDF5, hepfile stands for Heterogeneous
Entries in Parallel-file.

See hepfile.readthedocs.io for detailed documentation!
"""
from __future__ import annotations
import sys

from ._version import __version__

__all__ = ("__version__",)

from hepfile.read import *
from hepfile.write import *
import hepfile.dict_tools

if "awkward" in sys.modules:
    import hepfile.awkward_tools

if "pandas" in sys.modules:
    import hepfile.df_tools
    import hepfile.csv_tools
