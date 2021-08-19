import awkward as ak
import hepfile.write 
import hepfile.read 
import numpy as np

################################################################################
#def unpack_awkward_arrays(data,keys):
def unpack_awkward_arrays(data,groups=None,datasets=None):

    #data,event = read.load(infilename)

    #if type(keys) is not list:
    #    keys = [keys]

    alldatasets = data['_LIST_OF_DATASETS_']
    allgroups = []
    for d in alldatasets:
        if d.find('/')>=0:
            allgroups.append(d.split('/')[0])

    allgroups = np.unique(allgroups)
    
    ak_arrays = {}

    for group in groups:
        print("group: ",group)
        ak_arrays[group] = {}
        #topkey = key.split('/')[0]
        #nkey = topkey + "/n"  + topkey
        for dataset in alldatasets:
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
                if type(vals[0]) is str:
                    vals = vals.astype(str)
                ak_array = ak.unflatten(vals,num)
                datasetname = dataset.split(group+'/')[-1]
                ak_arrays[group][datasetname] = ak_array

    return ak_arrays

################################################################################
'''
def pack_coffea_awkward_arrays(data,awkward_arrays,new_entries=True,names=None):

    if names is None:
        print("The names for the groups must be provided!")
        print("Nothing will be written!")
        return -1
    
    if type(awkward_arrays) is not list:
        awkward_arrays = [awkward_arrays]

    for arr,groupname in zip(awkward_arrays,names):
        write.create_group(data, groupname, counter="n"+groupname)
        for field in arr.fields:



    return 1
'''
