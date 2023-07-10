"""
A file description modeled after the ROOT analysis toolkit and common use-cases
in High Energy Physics. Implemented in HDF5, hepfile stands for Heterogeneous
Entries in Parallel-file.

See hepfile.readthedocs.io for detailed documentation!
"""
from __future__ import annotations
import sys

from ._version import __version__
from .errors import MissingOptionalDependency

# explicitly set the package variable to ensure relative import work
__package__ = "hepfile"

# set some other module wide attributes
_AWKWARD = False
_PANDAS = False

# import modules
from hepfile.read import *
from hepfile.write import *
import hepfile.dict_tools

try:
    import hepfile.awkward_tools

    _AWKWARD = True
except ImportError:
    pass

try:
    import hepfile.df_tools
    import hepfile.csv_tools

    _PANDAS = True
except ImportError:
    pass

# put all these variables in __all__
__all__ = ("__version__", "__package__", "_AWKWARD", "_PANDAS")


# override getattr
def __getattr__(name: str) -> bool:
    if name == "_AWKWARD":
        return _AWKWARD
    if name == "_PANDAS":
        return _PANDAS

    if not _AWKWARD and name == "awkward_tools":
        raise MissingOptionalDependency("awkward")

    if not _PANDAS and name == "csv_tools" or name == "df_tools":
        raise MissingOptionalDependency("pandas")

    raise AttributeError
