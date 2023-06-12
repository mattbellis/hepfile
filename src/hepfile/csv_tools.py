'''
Tools to help with managing csvs with hepfile
'''

import numpy as np
import pandas as pd
import awkward as ak
import hepfile as hf
from typing import Optional

def csv_to_awkward(csvpaths:list[str], common_key:str, group_names:Optional[list]=None) -> ak.Record:
    '''
    Convert a list of csvs to an awkward array. 
    This is really just used in a step to convert csvs to a hepfile
    
    Args:
        csvpaths (list[str]): list of absolute paths to the csvs to convert to a hepfile
        common_key (str): The above list of csvs should have a common column name, give the name of this column
        group_names (list): the names for the groups in the hepfile. Default is None and the groups are based on the filenames
    
    Returns:
        Awkward array record of the csvs
    '''
    
    if group_names is None:
        group_names = [os.path.split(file) for file in csvpaths]

    for_ak = {}
    for f, group_name in zip(csvpaths, group_names):

        csv = pd.read_csv(f)

        groups = csv.groupby(common_key)
        split_groups = []
        for item in groups.groups:
            split_groups.append(groups.get_group(item))

        subdict = {}
        for grouping in split_groups:
            for colname in grouping.columns:
                if colname in subdict.keys():
                    subdict[colname].append(list(grouping[colname].values))
                else:
                    subdict[colname] = [list(grouping[colname].values)]

        for key in subdict.keys():
            subdict[key] = ak.Array(subdict[key])

        for_ak[group_name] = subdict
        
    return ak.Record(for_ak)

def csv_to_hepfile(csvpaths: list[str], common_key: str, outfile:Optional[str]=None, group_names:Optional[list]=None, write_hepfile:bool=True) -> dict:
    '''
    Convert a list of csvs to a hepfile
    
    This is helpful for converting database-like csvs to a hepfile where 
    each input csv has a common key and can be combined into a large table.
    
    Args:
        csvpaths (list[str]): list of absolute paths to the csvs to convert to a hepfile
        common_key (str): The above list of csvs should have a common column name, give the name of this column
        outfile (str): The output file name, if None data is written to the first filepath in csvpaths with 'csv' replaced with 'h5'
        group_names (list): the names for the groups in the hepfile. Default is None and the groups are based on the filenames
        write_hepfile: (bool): if True, write the hepfile. Default is True. 
        
    Returns:
        Dictionary of hepfile data
    '''
    
    if outfile is None:
        outpath = csvpath[0]
        outfile = outpath.replace('.csv', '.h5')
        
    awk = csv_to_awkward(csvpaths, common_key, group_names=group_names)
    
    return hf.awkward_tools.awkward_to_hepfile(awk, outfile=outfile, write_hepfile=write_hepfile)
