'''
Functions to help convert dictionaries into hepfiles
'''
import awkward as ak
import hepfile as hf

def dictlike_to_hepfile(dict_list, outfile, **kwargs):
    '''
    This wraps on `hepfile.awkward_tools.awkward_to_hepfile` to write a list of dictionaries to a hepfile.
    
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
    
    # validate input dictionary
    keys = dict_list[0].keys()
    for item in dict_list:
        if item.keys() != keys:
            raise IOError('Keys must match across the entire input dictionary list!!!')
    
    # convert dictionary list to  an awkward array and write to hepfile
    out_ak = ak.Array(dict_list)
    #hf.awkward_tools.awkward_to_hepfile(out_ak, outfile, **kwargs)
    hf.awkward_tools.awkward_to_hepfile(out_ak, outfile, **kwargs)
    return out_ak

def append(ak_dict, new_dict):
    '''
    Append a new event to an existing awkward dictionary with events
    
    Args:
        ak_dict (dict): Dictionary of awkward arrays
        new_dict (dict): Dictionary of value to append to ak_dict. All keys must match ak_dict!
    Return:
        Dictionary of awkward arrays with the new_dict appended
    '''
    if list(new_dict.keys()) != ak_dict.fields:
        raise Exception('Keys of new array do not match keys of existing array!')
        
    ak_list = ak.to_list(ak_dict)
    ak_list.append(new_dict)
    return ak.Array(ak_list)
