import os, glob
import pandas as pd
import numpy as np
import hepfile as hf

def test_csv_to_hepfile():
    '''
    Test case for hepfile.csv_tools.csv_to_hepfile
    '''

    # do the conversion using some example csvs
    datapath = os.path.join('docs', 'example_nb', '*.csv')
    files = glob.glob(datapath)
    common_key = 'Household ID'
    group_names = ['People', 'Residences', 'Vehicles']
    
    filename, data = hf.csv_tools.csv_to_hepfile(files, common_key, outfile='test-csv.h5', group_names=group_names)

    # check that they are consistent
    for group in group_names:
        assert group in data['_GROUPS_'].keys()
        assert 'Household ID' in data['_GROUPS_'][group]

    assert 'Age' in data['_GROUPS_']['People']

    # read in the people csv and check data integrity
    people = pd.read_csv(files[0])

    assert np.all(np.array(data['People/Height']) == np.array(people['Height']))
    assert np.all(np.array(data['People/Gender ID']) == np.array(people['Gender ID']))
