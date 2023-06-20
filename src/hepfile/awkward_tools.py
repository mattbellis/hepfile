from __future__ import annotations

import warnings
import awkward as ak
import numpy as np
from .write import *
from .constants import protected_names 

################################################################################
def hepfile_to_awkward(data:dict, groups:list=None, datasets:list=None) -> ak.Record:
    '''
    Converts all (or a subset of) the output data from `hepfile.read.load` to 
    a dictionary of awkward arrays.
    
    Args:
        data (dict): Output data dictionary from the `hepfile.read.load` function.
        groups (list): list of groups to pull from data and convert to awkward arrays.
        datasets (list): list of datasets to pull from data and include in the awkward arrays.
        
    Returns:
        ak_arrays (dict): dictionary of awkward arrays with the data.
    '''
    
    if datasets is None:
        datasets = data['_LIST_OF_DATASETS_']
    
    if groups is None:
        groups = list(data['_GROUPS_'].keys())
    
    ak_arrays = {}

    # turn a few things into sets for faster searching
    list_of_counters = set(data['_LIST_OF_COUNTERS_'])
    singletons_group = set(data['_SINGLETONS_GROUP_'])

    for group in groups:
        for dset in data['_GROUPS_'][group]:

            dataset = f'{group}/{dset}'
            
            if dataset in list_of_counters: continue

            if dset in singletons_group:
                ak_arrays[dset] = ak.Array(data[dset])
                continue                   
                
            nkey = data['_MAP_DATASETS_TO_COUNTERS_'][dataset]
                
            num = data[nkey]
            vals = data[dataset]
            
            if len(vals) > 0 and type(vals[0]) is str:
                vals = vals.astype(str)
            ak_array = ak.unflatten(list(vals),list(num))

            if group not in ak_arrays.keys():
                ak_arrays[group] = {}
            ak_arrays[group][dset] = ak_array

    try:
        awk = ak.Array(ak_arrays)
    except ValueError as e:
        warnings.warn('Cannot convert to an Awkward Array because dict arrays have different lengths! Returning an Awkward Record instead.')
        awk = ak.Record(ak_arrays)

    try:
        _is_valid_awkward(awk)
    except IOError as e:
        print(e)
        raise ValueError('Cannot convert to proper awkward array because of the above error! Check your input hepfile format')
    
    return awk

################################################################################
def awkward_to_hepfile(ak_array:ak.Record, outfile:str=None, write_hepfile:bool=True, **kwargs) -> dict:
    '''
    Converts a dictionary of awkward arrays to a hepfile

    Args:
        ak_array (Awkward Array): dictionary of Awkward Arrays to write to a hepfile
        outfile (str): path to write output hdf5 file to
        write_hepfile (bool): if True, writes data to outfile. If False, just converts to hepfile format and returns
        **kwargs (None): Passed to `hepfile.write.write_to_file`

    Returns:
        Dictionary of hepfile data
    '''

    # perform IO checks

    _is_valid_awkward(ak_array)
    
    if write_hepfile == True and outfile is None:
        raise IOError('Please provide an outfile path if write_hepfile=True!')

    if write_hepfile == False and outfile is not None:
        warnings.warn('You set write_hepfile to False but provided an output file path. This output file path will not be used!')
    
    data = initialize()
    singleton = False

    for group in ak_array.fields:
        
        counter = f'n{group}'
        counter_key = f'{group}/{counter}'
        
        if len(ak_array[group].fields) == 0:
            singleton = True
            
            dtype = _get_awkward_type(ak_array[group])
            create_dataset(data, group, dtype=dtype)

            data[group] = ak_array[group]
            continue
    
        create_group(data, group, counter=counter)
        for ii, dataset in enumerate(ak_array[group].fields):

            if len(ak_array[group][dataset][0]) == 0:
                dtype = None
            else:
                dtype = _get_awkward_type(ak_array[group][dataset])

            create_dataset(data, dataset, group=group, dtype=dtype)
            
            # check if dataset name has /'s in it
            if dataset.find('/') >= 0:
                dataset_name = dataset.replace('/', '-')
            else:
                dataset_name = dataset
                
            name = f'{group}/{dataset_name}'
            for data_subset in ak_array[group][dataset]:
                data[name].append(data_subset)
                if ii == 0:
                    data[counter_key].append(len(data_subset))            
            
            data[name] = ak.flatten(ak.Array(data[name]))
    
        data[counter_key] = ak.Array(data[counter_key])
    
    if len(data['_GROUPS_']['_SINGLETONS_GROUP_']) > 1:
        data['_SINGLETONS_GROUP_/COUNTER'] = [1]*len(data[data['_GROUPS_']['_SINGLETONS_GROUP_'][1]])

    if write_hepfile:
        print("Writing the hdf5 file from the awkward array...")
        hdfile = write_to_file(outfile,data)

    return data

def _awkward_depth(ak_array:ak.Record) -> int:

    max_depth = 0
    for item in ak_array.to_list():
        item_depth = -1
        for s in str(item):
            if s == "{":
                item_depth += 1
            if s == "}":
                item_depth -= 1
        if item_depth > max_depth:
            max_depth = item_depth

    return max_depth

def _is_valid_awkward(ak_array:ak.Record):
    '''
    Checks if the input awkward array is valid and raises an exception if not
    
    Args:
        ak_array (ak.Array): awkward array to check    
    '''

        # validate input array
    if not isinstance(ak_array, ak.Array) and not isinstance(ak_array, ak.Record):
        raise IOError('Please input an Awkward Array or Awkward Record')
        
    if ak_array.fields == 0:
        raise IOError('Your input Awkward Array must be a Record. This means it needs to have fields in it.')

    # check input array only has a "depth" of 2
    # this can be removed once hepfiles support unlimited depth of groups!
    if _awkward_depth(ak_array) > 2:
        raise IOError('Hepfile only supports awkward arrays with a depth <= 2! Please ensure your input follows this guideline.')


def _get_awkward_type(ak_array:ak.Record) -> type:

    ndim = ak_array.ndim
    if ndim > 2 or ndim < 1:
        raise ValueError('Cannot check type with depth > 2 or depth <1')
    
    if ndim == 1:
        return type(ak_array[0])
    else:
        return type(ak_array[0][0])
