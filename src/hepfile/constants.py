"""
Some constants used in the rest of the package
"""

# set of names that can not be used in group or dataset names
protected_names = {
    "_PROTECTED_NAMES_",
    "_GROUPS_",
    "_MAP_DATASETS_TO_COUNTERS_",
    "_MAP_DATASETS_TO_DATA_TYPES_",
    "_LIST_OF_COUNTERS_",
    "_SINGLETONS_GROUP_",
    "_SINGLETONS_GROUP_/COUNTER",
    "_META_",
    "_HEADER_",
    "_SINGLETONSGROUPFORSTORAGE_",
}

# NumPy Character Codes that can be stored in HDF5 files
char_codes = {"i", "u", "f", "c"}
