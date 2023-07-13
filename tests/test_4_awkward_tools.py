import hepfile as hf
import awkward as ak
import numpy as np
import pytest

def test_hepfile_to_awkward():
    '''
    Tests hf.awkward_tools.hepfile_to_awkward
    '''

    # read in the testing file
    testfile = "FOR_TESTS.hdf5"
    hepfile, meta = hf.load(testfile)

    # convert
    awk = hf.awkward_tools.hepfile_to_awkward(hepfile)
    print(awk)
    
    # check that the data is consistent

    # first check that the first level keys are all good in the awkward array
    assert "jet" in awk.fields
    assert "muons" in awk.fields
    assert "METpx" in awk.fields
    assert "METpy" in awk.fields
    
    # check the second level keys
    for group in hepfile['_GROUPS_'].keys():
        for key in hepfile['_GROUPS_'][group]:
            if f'{group}/{key}' == hepfile['_MAP_DATASETS_TO_COUNTERS_'][group]: continue
            if group == '_SINGLETONS_GROUP_':
                assert key in awk.fields
            else:
                assert key in awk[group].fields

    # check that the data is the same for a few of them
    assert ak.all(hepfile['METpx'] == awk.METpx)
    assert ak.all(hepfile['METpy'] == awk.METpy)
    assert ak.all(hepfile['jet/e'] == ak.flatten(awk.jet.e))
    assert ak.all(hepfile['muons/px'] == ak.flatten(awk.muons.px))

    # trigger an Awkward Structure Error
    with pytest.raises(hf.errors.AwkwardStructureError):
        data = hf.initialize()
        hf.create_dataset(data, 'x')
        data['x'] = {'y': np.array([b'1']),
                     'w':{'z':{'y':np.array([b'1']), 'i':[b'2']}}}
        a = hf.awkward_tools.hepfile_to_awkward(data)

    # try just converting a subset of groups and datasets
    awk_subset = hf.awkward_tools.hepfile_to_awkward(hepfile,
                                                     groups='jet',
                                                     datasets=['jet/e', 'jet/px'])
    assert 'jet' in  awk_subset.fields
    assert 'muons' not in awk_subset.fields
    assert 'METpx' not in awk_subset.fields
    assert 'METpy' not in awk_subset.fields
    assert ak.all(hepfile['jet/e'] == ak.flatten(awk.jet.e))

    # convert with some weird data types
    data = hf.initialize()
    hf.create_group(data, 'x', counter='n_x')
    hf.create_dataset(data, ['y', 'z', 'w', 'a'], group='x', dtype=str)
    bucket = hf.create_single_bucket(data)
    bucket['x/y'] = np.array([b'1'])
    bucket['x/z'] = [b'1']
    bucket['x/w'] = ['1']
    bucket['x/a'] = np.array(['1'])
    hf.pack(data, bucket)

    a = hf.awkward_tools.hepfile_to_awkward(data)

    assert isinstance(ak.to_list(a.x.z)[0][0], str)
    assert isinstance(ak.to_list(a.x.y)[0][0], str)
    assert isinstance(ak.to_list(a.x.w)[0][0], str)
    assert isinstance(ak.to_list(a.x.a)[0][0], str)
    
def test_awkward_to_hepfile():
    '''
    Tests hf.awkward_tools.awkward_to_hepfile
    '''

    # read in the test data
    testfile = "FOR_TESTS.hdf5"
    data, meta = hf.load(testfile)

    # convert it to an awkward array (this has already been tested so should be safe)
    awk = hf.awkward_tools.hepfile_to_awkward(data)
    
    # now try converting it back to a hepfile
    newdata = hf.awkward_tools.awkward_to_hepfile(awk, write_hepfile=False)
    
    # check that they are the same
    assert ak.all(data['METpy'] == newdata['METpy'])
    assert ak.all(data['METpx'] == newdata['METpx'])
    assert ak.all(data['jet/e'] == newdata['jet/e'])
    assert ak.all(data['muons/px'] == newdata['muons/px'])
    assert ak.all(ak.sort(data['_GROUPS_']['jet']) == ak.sort(newdata['_GROUPS_']['jet']))

    # raise some errors
    with pytest.raises(hf.errors.InputError):
        hf.awkward_tools.awkward_to_hepfile(awk, write_hepfile=True)

    with pytest.raises(hf.errors.AwkwardStructureError):
        hf.awkward_tools.awkward_to_hepfile([])

    with pytest.raises(hf.errors.AwkwardStructureError):
        hf.awkward_tools.awkward_to_hepfile(ak.Array[1])

def test_get_awkward_type():

    with pytest.raises(hf.errors.InputError):
        hf.awkward_tools._get_awkward_type(ak.Array([]))

    with pytest.raises(hf.errors.InputError):
        t = hf.awkward_tools._get_awkward_type(ak.Array([np.array(['1']), np.array([1,2])]))
    
def test_is_valid_awkward():

    with pytest.raises(hf.errors.AwkwardStructureError):
        hf.awkward_tools._is_valid_awkward(ak.Array(['x']))

    with pytest.raises(hf.errors.AwkwardStructureError):
        hf.awkward_tools._is_valid_awkward(np.array([1]))
