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

    return ak.Array(ak_arrays)

################################################################################
def awkward_to_hepfile(ak_array, outfile, **kwargs):
    '''
    Converts a dictionary of awkward arrays to a hepfile

    Args:
        ak_array (Awkward Array): dictionary of Awkward Arrays to write to a hepfile
        outfile (str): path to write output hdf5 file to
        **kwargs (None): Passed to `hepfile.write.write_to_file`
    '''

    # validate input array
    if type(ak_array) != ak.Array:
        raise IOError('Please input an Awkward Array Record')
        
    if ak_array.fields == 0:
        raise IOError('Your input Awkward Array must be a Record. This means it needs to have fields in it.')

    # check input array only has a "depth" of 2
    # this can be removed once hepfiles support unlimited depth of groups!
    if _awkward_depth(ak_array) > 2:
        raise IOError('Hepfile only supports awkward arrays with a depth <= 2! Please ensure your input follows this guideline.')
    
    data = hf.write.initialize()
    singleton = False

    for group in ak_array.fields:
        
        counter = f'n{group}'
        counter_key = f'{group}/{counter}'
        if len(ak_array[group].fields) == 0:
            singleton = True
            hf.write.create_dataset(data, group)
            data[group] = ak_array[group]
            continue
    
        hf.write.create_group(data, group, counter=counter)
        hf.write.create_dataset(data, list(ak_array[group].fields), group=group)
        for ii, dataset in enumerate(ak_array[group].fields):

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


def _awkward_depth(ak_array):

    max_depth = 0
    for item in ak_array.to_list():
        item_depth = -1
        for s in str(item):
            if s == "{":
                item_depth += 1
        if item_depth > max_depth:
            max_depth = item_depth

    return max_depth
