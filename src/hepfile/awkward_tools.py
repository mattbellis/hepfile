import awkward as ak
import numpy as np
import hepfile as hf

################################################################################
#def unpack_awkward_arrays(data,keys):
def hepfile_to_awkward(data,groups=None,datasets=None):
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
        
    print(groups, datasets)
    
    ak_arrays = {}

    for group in groups:
        ak_arrays[group] = {}
        for dataset in datasets:
            if dataset.find(group)>=0:
                
                if dataset in data['_LIST_OF_COUNTERS_'] or dataset == group:
                    if dataset in data['_SINGLETONS_GROUP_']:
                        ak_arrays[group] = ak.Array(data[dataset])
                    continue                   

                nkey = data['_MAP_DATASETS_TO_COUNTERS_'][dataset]
                
                num = data[nkey]
                vals = data[dataset]

                if len(vals) > 0 and type(vals[0]) is str:
                    vals = vals.astype(str)
                ak_array = ak.unflatten(list(vals),list(num))
                datasetname = dataset.split(group+'/')[-1]
                ak_arrays[group][datasetname] = ak_array

    return ak_arrays

################################################################################

def awkward_to_hepfile(ak_array, outfile, **kwargs):
    '''
    Converts a dictionary of awkward arrays to a hepfile

    Args:
        ak_array (Awkward Array): dictionary of Awkward Arrays to write to a hepfile
        outfile (str): path to write output hdf5 file to
        **kwargs (None): Passed to `hepfile.write.write_to_file`
    '''

    data = hf.write.initialize()
    singleton = False

    for group in ak_array.keys():
        
        counter = f'n{group}'
        counter_key = f'{group}/{counter}'
    
        if type(ak_array[group]) == ak.Array:
            singleton = True
            hf.write.create_dataset(data, group)
            data[group] = ak_array[group]
            continue
    
        hf.write.create_group(data, group, counter=counter)
        hf.write.create_dataset(data, list(ak_array[group].keys()), group=group)
    
        for ii, dataset in enumerate(ak_array[group].keys()):

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
        
    print("Writing the hdf5 file from the awkward array...")
    hdfile = hf.write_to_file(outfile,data,force_single_precision=False)

def _append_to_awkward(ak_array, new_val):
    '''
    Allows for appending to an awkward array
    
    Args:
        ak_array (Awkward Array): Awkward array to append to
        new_val (any): value to append to the awkward array
    Return:
        Awkward Array with new value appended
    '''
    ak_list = ak.to_list(ak_array) # convert to list
    ak_list.append(new_val) # append to list
    return ak.Array(ak_list) # return an awkward array

