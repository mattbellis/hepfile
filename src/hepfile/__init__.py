"""
A file description modeled after the ROOT analysis toolkit and common use-cases in High Energy Physics. Implemented in HDF5, hepfile stands for Heterogeneous Entries in Parallel-file. 
"""

__version__ = "0.1.3"

__all__ = ("__version__",)

from hepfile.read import *
from hepfile.write import *
import hepfile.awkward_tools
import hepfile.dict_tools
import hepfile.csv_tools
