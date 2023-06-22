'''
Custom exception messages
'''
class InputError(Exception):
    '''
    General error to describe when the input value of a function
    in the module is either the wrong type or incorrectly formatted.
    '''
    pass

class AwkwardStructureError(Exception):
    '''
    Thrown when the structure of an Awkward Array is not appropriate
    for the future processing.
    '''
    pass

class DictStructureError(Exception):
    '''
    Thrown when the structure of a dictionary is not appropriate for
    the future processing.
    '''
    pass

class RangeSubsetError(Exception):
    '''
    Thrown when the input range is incorrectly formatted. See the
    error for more details about what exactly is incorrect.
    '''
    pass

class MetadataNotFound(Exception):
    '''
    Thrown when there is no metadata found for a hepfile even
    though the user has requested it.
    '''
    pass

class HeaderNotFound(Exception):
    '''
    Thrown when there is no header found for a hepfile even
    though the user has requested it.
    '''
    pass

class DatasetSizeDiscrepancy(Exception):
    '''
    Thrown when two datasets under one group do not have the same
    length. This is usually not appropriate for hepfiles.
    '''
    pass

class MissingSingletonValue(Exception):
    '''
    Thrown when we try to pack a bucket into a hepfile data dictionary
    and no singleton value is found in the new bucket.
    '''
    pass
