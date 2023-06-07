'''
Functions to help convert dictionaries into hepfiles
'''
import awkward as ak
import hepfile as hf

def dictlike_to_hepfile(dict_list, outfile):
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
    hf.awkward_tools.awkward_to_hepfile(out_dict, outfile)
