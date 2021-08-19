import awkward as ak
import write as h5hepwrite

################################################################################
def unpack_awkward_arrays(data,keys):

    if type(keys) is not list:
        keys = [keys]

    ak_arrays = []

    for topkey in keys:
        topkey = key.split('/')[0]
        nkey = topkey + "/n"  + topkey
        num = data[nkey]
        vals = data[key]
        ak_array = ak.unflatten(vals,num)
        ak_arrays.append(ak_array)

    return ak_arrays

################################################################################
def pack_coffea_awkward_arrays(data,awkward_arrays,new_entries=True,names=None):

    if names is None:
        print("The names for the groups must be provided!")
        print("Nothing will be written!")
        return -1
    
    if type(awkward_arrays) is not list:
        awkward_arrays = [awkward_arrays]

    for arr,groupname in zip(awkward_arrays,names):
        h5hepwrite.create_group(data, groupname, counter="n"+groupname)
        for field in arr.fields:



    return 1
