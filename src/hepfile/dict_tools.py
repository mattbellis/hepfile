'''
Functions to help convert dictionaries into hepfiles
'''
import awkward as ak
import hepfile as hf

def dictlike_to_hepfile(dict_list, outfile, **kwargs):
    '''
    Writes a list of dictlike object to a hepfile. Must have a specific format:
    - each dictlike object is a "event"
    - first level of dict keys are the groups
    - second level of dict keys are the datasets
    - entries in second level of dict object is the data and can be either awkward arrays or lists
    - data entries in the first level of the dict are singleton objects

    Args:
        dict_list (list): list of dictionaries where each dictionary holds information on an event
        outfile (str): path to write output hepfile to
        **kwargs: passed to `hepfile.write.write_to_file`
    Returns:
        Dictionary of Awkward Arrays with the data stored in outfile
    '''

    out_dict = {}
    for item in dict_list:
        
        # check that this is dict like
        try:
            k = item.keys()
        except AttributeError:
            raise IOError('Input dict_list is not well-formed!')
        
        for key in item.keys():        
            if key not in out_dict.keys():
                if type(item[key]) != dict:
                    out_dict[key] = []
                else:
                    out_dict[key] = {}
                    
            if type(out_dict[key]) == list:
                out_dict[key].append(item[key])
                continue
                    
            for subkey in item[key].keys():
                if subkey not in out_dict[key].keys():
                    out_dict[key][subkey] = []
                out_dict[key][subkey].append(item[key][subkey])
                                
    for key in out_dict.keys():
        
        if type(out_dict[key]) == list:
            out_dict[key] = ak.Array(out_dict[key])
            continue
        
        for subkey in out_dict[key].keys():
            out_dict[key][subkey] = ak.Array(out_dict[key][subkey])
    
    # convert the awkward array to a hepfile and write it out
    hf.awkward_tools.awkward_to_hepfile(out_dict, outfile, **kwargs)
    return out_dict

def append(ak_dict, new_dict):
    '''
    Append a new event to an existing awkward dictionary with events
    
    Args:
        ak_dict (dict): Dictionary of awkward arrays
        new_dict (dict): Dictionary of value to append to ak_dict. All keys must match ak_dict!
    Return:
        Dictionary of awkward arrays with the new_dict appended
    '''
    if new_dict.keys() != ak_dict.keys():
        raise Exception('Keys of new array do not match keys of existing array!')

    keys = new_dict.keys()
    for key in keys:

        if type(new_dict[key]) != dict:
            # this is a singleton
            ak_dict[key] = hf.awkward_tools._append_to_awkward(ak_dict[key], new_dict[key])
            continue

        subkeys = new_dict[key].keys()
        if subkeys != ak_dict[key].keys():
            raise Exception(f'Keys of new array do not match existing array for sub-dictionary {key}') 

        for subkey in subkeys:
            ak_dict[key][subkey] = hf.awkward_tools._append_to_awkward(ak_dict[key][subkey], new_dict[key][subkey])
    
    return ak_dict
