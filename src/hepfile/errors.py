'''
Custom exception messages
'''

class InputError(Exception):
    pass

class AwkwardStructureError(Exception):
    pass

class DictStructureError(Exception):
    pass

class RangeSubsetError(Exception):
    pass

class MetadataNotFound(Exception):
    pass

class DatasetSizeDiscrepancy(Exception):
    pass

class MissingSingletonValue(Exception):
    pass
