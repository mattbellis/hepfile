import os, glob
import pandas as pd
import numpy as np
import hepfile as hf
import pytest

def test_csv_to_hepfile():
    '''
    Test case for hepfile.csv_tools.csv_to_hepfile
    '''

    # do the conversion using some example csvs
    filedir = os.path.join('docs', 'example_nb')
    datapath = os.path.join(filedir, '*.csv')
    files = glob.glob(datapath)
    common_key = 'Household ID'
    
    with pytest.warns(UserWarning):
        filename, data = hf.csv_tools.csv_to_hepfile(files, common_key, outfile='test-csv.h5')
    
    # check that they are consistent
    group_names = ['People.csv', 'Residences.csv', 'Vehicles.csv']
    for group in group_names:
        assert group in data['_GROUPS_'].keys()

    assert 'Household ID' in data['_GROUPS_']['_SINGLETONS_GROUP_']

    assert 'Age' in data['_GROUPS_']['People.csv']

    # read in the people csv and check data integrity
    people = pd.read_csv(os.path.join('docs', 'example_nb', 'People.csv'))

    assert np.all(np.array(data['People.csv/Height']) == np.array(people['Height']))
    assert np.all(np.array(data['People.csv/Gender ID']) == np.array(people['Gender ID']))

    # try passing it no outfile name to make sure that works too
    with pytest.warns(UserWarning):
        filename, data = hf.csv_tools.csv_to_hepfile(files, common_key)

    assert files[0].replace('.csv', '.h5') in glob.glob(os.path.join(filedir,'*.h5'))
