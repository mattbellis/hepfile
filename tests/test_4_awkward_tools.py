import hepfile as hf
import awkward as ak

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
    print(data['_GROUPS_'], newdata['_GROUPS_'])
    # check that they are the same
    assert ak.all(data['METpy'] == newdata['METpy'])
    assert ak.all(data['METpx'] == newdata['METpx'])
    assert ak.all(data['jet/e'] == newdata['jet/e'])
    assert ak.all(data['muons/px'] == newdata['muons/px'])
    assert ak.all(ak.sort(data['_GROUPS_']['jet']) == ak.sort(newdata['_GROUPS_']['jet']))
