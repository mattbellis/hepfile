"""
A file description modeled after the ROOT analysis toolkit and common use-cases in High Energy Physics.
Implemented in HDF5, hepfile stands for Heterogeneous Entries in Parallel-file.

See hepfile.readthedocs.io for detailed documentation!
"""
from __future__ import annotations

__version__ = "0.1.3"

__all__ = ("__version__",)

from hepfile.read import *
from hepfile.write import *
import hepfile.awkward_tools
import hepfile.dict_tools
import hepfile.csv_tools
import hepfile
