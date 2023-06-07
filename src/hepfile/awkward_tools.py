import awkward as ak
import hepfile.write 
import hepfile.read 
import numpy as np

################################################################################
#def unpack_awkward_arrays(data,keys):
def hepfile_to_awkward(data,groups=None,datasets=None):
    '''
    Converts all (or a subset of) the output data from `hepfile.read.load` to 
    a dictionary of awkward arrays.
    
    Args:
        **data** (dict): Output data dictionary from the `hepfile.read.load` function.
        **groups** (list): list of groups to pull from data and convert to awkward arrays.
        **datasets** (list): list of datasets to pull from data and include in the awkward arrays.
        
    Returns:
        **ak_arrays** (dict): dictionary of awkward arrays with the data.
    '''
    
    protected_names = ["_PROTECTED_NAMES_",
                       "_GROUPS_",
                       "_MAP_DATASETS_TO_COUNTERS_",
                       "_MAP_DATASETS_TO_DATA_TYPES_"
                       "_LIST_OF_COUNTERS_",
                       "_SINGLETONS_GROUP_",
                       "_SINGLETONS_GROUP_/COUNTER"
                      ]
    
    if datasets is None:
        datasets = data['_LIST_OF_DATASETS_']
    
    allgroups = []
    for d in datasets:
        if d not in protected_names:
            allgroups.append(d.split('/')[0])
    
    if groups is None:
        groups = np.unique(allgroups)
    
    ak_arrays = {}

    for group in groups:
        print("group: ",group)
        ak_arrays[group] = {}
        for dataset in datasets:
            dataset = group + '/' + dataset
            if dataset.find(group)>=0:

                print("dataset: ",dataset)

                if dataset in data['_LIST_OF_COUNTERS_'] or \
                   dataset == group:
                    continue

                nkey = data['_MAP_DATASETS_TO_COUNTERS_'][dataset]
                print('nkey: ',nkey)
                num = data[nkey]
                vals = data[dataset]
                print(vals)
                print(num)
                if len(vals) > 0 and type(vals[0]) is str:
                    vals = vals.astype(str)
                ak_array = ak.unflatten(list(vals),list(num))
                datasetname = dataset.split(group+'/')[-1]
                ak_arrays[group][datasetname] = ak_array

    return ak_arrays

################################################################################

def awkward_to_hepfile(data,awkward_arrays,new_entries=True,names=None):
    '''
    Converts a dictionary of awkward arrays to a hepfile
    '''
    return None

