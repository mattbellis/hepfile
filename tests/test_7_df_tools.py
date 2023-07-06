'''
Tests for df_tools.py
'''
import numpy as np
import pandas as pd
import awkward as ak
import hepfile as hf

def io(return_type='classic'):
    '''
    wrapper to load in data for testing

    Args:
        return_type: classic is the classic data object, awkward is an awkward array
    Returns:
        either dict or awkward array of data
    '''

    if return_type == 'awkward':
        data, _ = hf.load('FOR_TESTS.hdf5', return_awkward=True)
    else:
        data, _ =  hf.load('FOR_TESTS.hdf5')
    return data
        
def test_hepfile_to_df():
    '''
    Test hepfile to dataframe
    '''

    data = io() # read in the data
    # put the data in a list of dataframes
    dfs = hf.df_tools.hepfile_to_df(data)

    # make sure structure looks like it should
    groups = data['_GROUPS_'].keys()
    assert all(key in groups for key in dfs.keys())

    # make sure data matches
    assert np.all(data['METpx'] == dfs['_SINGLETONS_GROUP_']['METpx'])
    assert np.all(data['jet/pz'] == dfs['jet']['pz'])
    assert np.all(data['muons/py'] == dfs['muons']['py'])

    # translate a subset with just one group
    dfs = hf.df_tools.hepfile_to_df(data, groups='jet')
    assert isinstance(dfs, pd.DataFrame)
    assert 'event_num' in dfs.columns 
    
    cols = list(dfs.columns)
    cols.remove('event_num')
    groups = list(data['_GROUPS_']['jet'])
    groups.remove('njet')
    assert np.all(sorted(cols) == sorted(groups))

    # check data integrity
    assert np.all(dfs.e == data['jet/e'])

    # now check with a subset
    dfs = hf.df_tools.hepfile_to_df(data, events=1, groups='jet')

    assert len(dfs.event_num.unique()) == 1
    assert dfs.event_num.unique() == 1
    
def test_awkward_to_df():
    '''
    Test awkward_to_df
    '''
    data = io(return_type='awkward') # read in the data

    # put the data in a list of dataframes
    dfs = hf.df_tools.awkward_to_df(data)
    
    # make sure structure looks like it should
    assert all(key in data.fields for key in dfs.keys())

    # make sure data matches
    assert np.all(data['METpx'] == dfs['METpx']['values'].values)
    assert np.all(ak.flatten(data['jet']['pz']) == dfs['jet']['pz'].values)
    assert np.all(ak.flatten(data['muons']['py']) == dfs['muons']['py'].values)

    # translate a subset with just one group
    dfs = hf.df_tools.awkward_to_df(data, groups='jet')
    assert isinstance(dfs, pd.DataFrame)
    assert 'event_num' in dfs.columns 
    
    cols = list(dfs.columns)
    cols.remove('event_num')
    groups = list(data['jet'].fields)
    assert np.all(sorted(cols) == sorted(groups))

    # check data integrity
    assert np.all(dfs.e.values == ak.flatten(data['jet']['e']))

    # now check with a subset
    dfs = hf.df_tools.awkward_to_df(data, events=1, groups='jet')

    assert len(dfs.event_num.unique()) == 1
    assert dfs.event_num.unique() == 1    

def test_df_to_hepfile():
    '''
    Test df_to_hepfile
    '''

    # 1) load in the file, convert it to a dataframe,
    # then try to convert it back to hepfile
    data = io()
    dfs = hf.df_tools.hepfile_to_df(data)
    newdata = hf.df_tools.df_to_hepfile(dfs, write_hepfile=False)
    for key in newdata:
        if key == 'event_num': continue
        # the counters will not necessarily match because we lose and need to
        # re derive the names of those!
        if key in newdata['_MAP_DATASETS_TO_COUNTERS_'].values(): continue 
        assert key in data.keys()

    # check that the data is consistent
    assert np.all(np.sort(data['_GROUPS_']['jet']) == np.sort(newdata['_GROUPS_']['jet']))
    for datakey in ['jet/e', 'muons/e', 'METpx']:
        assert np.all(data[datakey] == data[datakey])

    # 2) write a file from scratch using this method
    x = pd.DataFrame({'a':[1,2,3],
                      'b':[4,5,6],
                      'c':[7,8,9],
                      'n':[0,0,1]})
    y = pd.DataFrame({'a':[4,5,6],
                      'b':[7,8,9],
                      'e':[10,11,12],
                      'n':[0,1,1]})

    d = hf.df_tools.df_to_hepfile({'x':x,'y':y}, write_hepfile=False, event_num_col='n')
    assert np.all(d['x/a'] == x['a'])
    assert np.all(d['y/a'] == y['a'])
    assert np.all(d['n'] == [0,1])
