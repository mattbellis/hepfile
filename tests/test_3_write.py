import numpy as np
import hepfile
import h5py as h5

import pytest
import time

import sys
sys.path.append('./scripts')
#from write_h5hep_file_for_unit_tests import write_h5hep_file_for_unit_tests

# sys.path.append('../src/hepfile')
#import write as hepfile
#import read as read

#from write_file_for_unit_tests import write_file_for_unit_tests


############################################################################
def isEmpty(dictionary):
    test = True
    print(dictionary.keys())
    for key in dictionary.keys():
        print(key)
        print(dictionary[key])
        print(type(dictionary[key]))
        if dictionary[key] is None:
            test = True
        elif type(dictionary[key]) == list or type(dictionary[key]) == np.ndarray:
            if len(dictionary[key]) > 0:
                test = False

    return test
################################################################################

################################################################################


def test_initialize():

    test_data = hepfile.initialize()

    print(test_data)

    assert isinstance(test_data, dict)
    assert test_data['_GROUPS_']['_SINGLETONS_GROUP_'] == ['COUNTER']
    assert test_data['_MAP_DATASETS_TO_COUNTERS_']['_SINGLETONS_GROUP_'] == '_SINGLETONS_GROUP_/COUNTER'
    assert test_data['_LIST_OF_COUNTERS_'] == ['_SINGLETONS_GROUP_/COUNTER']
    assert test_data['_SINGLETONS_GROUP_/COUNTER'] == []
################################################################################


################################################################################
def test_clear_bucket():

    # This assumes you run nosetests from the h5hep directory and not
    # the tests directory.
    filename = "FOR_TESTS.hdf5"
    desired_datasets = ['jet', 'muon']
    subset = 1000

    with pytest.warns(UserWarning):
        data, bucket = hepfile.load(filename, False, desired_datasets, subset)

    hepfile.clear_bucket(bucket)

    assert isEmpty(bucket) == True
################################################################################


################################################################################
def test_create_single_bucket():

    data = hepfile.initialize()

    hepfile.create_group(data, 'jet', counter='njet')
    hepfile.create_dataset(
        data, ['e', 'px', 'py', 'pz'], group='jet', dtype=float)

    hepfile.create_group(data, 'muons', counter='nmuon')
    hepfile.create_dataset(
        data, ['e', 'px', 'py', 'pz'], group='muons', dtype=float)

    test_bucket = hepfile.create_single_bucket(data)

    assert isEmpty(test_bucket) == False
    assert isinstance(test_bucket, dict)
################################################################################

################################################################################


def test_create_group():

    data = hepfile.initialize()
    hepfile.create_group(data, 'jet', counter='njet')

    assert isEmpty(data['_GROUPS_']) == False
    assert 'jet/njet' in data.keys()

    with pytest.warns(UserWarning):
        hepfile.create_group(data,"test/slash",counter='ntest/slash', verbose=True)

    assert 'test-slash' in data['_GROUPS_']
    assert 'test-slash/ntest-slash' in data.keys()

    # try adding a protected group
    with pytest.raises(hepfile.errors.InputError):
        hepfile.create_group(data, '_META_', counter='n')

    # try not giving a counter and catch the warning
    with pytest.warns(UserWarning):
        hepfile.create_group(data, 'test')

    # try adding a key that is already there
    with pytest.warns(UserWarning):
        hepfile.create_group(data, 'jet', counter='njet')

    
################################################################################

################################################################################

def test_pack():

    data = hepfile.initialize()
    hepfile.create_group(data, 'obj', counter='nobj')
    hepfile.create_dataset(data, ['myfloat'], group='obj', dtype=float)
    hepfile.create_dataset(data, ['myint'], group='obj', dtype=int)
    hepfile.create_dataset(data, ['mystr'], group='obj', dtype=str)
    hepfile.create_dataset(data, ['myarray'], group='obj', dtype=str)
    
    bucket = hepfile.create_single_bucket(data)

    # Normal packing test

    for i in range(5):
        bucket['obj/myfloat'].append(2.0)
        bucket['obj/myint'].append(2)
        bucket['obj/mystr'].append('two')
    bucket['obj/nobj'] = 5

    test = hepfile.pack(data, bucket)
    assert test is None 
    assert len(data['obj/myfloat']) == 5
    assert len(data['obj/myint']) == 5
    assert len(data['obj/mystr']) == 5
    assert data['obj/nobj'][0] == 5

    assert len(bucket['obj/myfloat']) == 0
    assert len(bucket['obj/myint']) == 0
    assert len(bucket['obj/mystr']) == 0
    assert bucket['obj/nobj'] == 0

    # AUTO_SET_COUNTER = False
    bucket['obj/myfloat'].append(2.0)
    bucket['obj/myint'].append(2)
    bucket['obj/mystr'].append('two')
    bucket['obj/myarray'] = np.array([1,2])
    
    # Is the mistake propagated?
    bucket['obj/nobj'] = 2

    hepfile.pack(data, bucket, AUTO_SET_COUNTER=False, verbose=True)
    assert data['obj/nobj'][1] == 2

    # Fix mistake
    data['obj/nobj'][1] = 2

    # STRICT_CHECKING = True
    bucket['obj/myfloat'].append(2.0)
    bucket['obj/myint'].append(2)
    # 1 != 0, strict checking should fail.

    with pytest.raises(hepfile.errors.DatasetSizeDiscrepancy):
        test = hepfile.pack(data, bucket, STRICT_CHECKING=True, verbose=True)
            
    # EMPTY_OUT_BUCKET = False

    bucket['obj/mystr'].append('two')

    hepfile.pack(data, bucket, EMPTY_OUT_BUCKET=False, verbose=True)

    assert isEmpty(bucket) == False

    #assert type(data['obj/mystr'][0]) is str


################################################################################


################################################################################
def test_create_dataset():

    data = hepfile.initialize()
    hepfile.create_group(data, 'jet', counter='njet')
    hepfile.create_dataset(
        data, ['e', 'px', 'py', 'pz'], group='jet', dtype=float, verbose=True)
    hepfile.create_dataset(data, 'METpx', dtype=int, verbose=True)

    assert isEmpty(data['_GROUPS_']) == False
    assert 'jet/njet' in data.keys()
    assert 'jet/e' in data.keys()
    assert 'jet/px' in data.keys()
    assert 'jet/e' in data['_MAP_DATASETS_TO_COUNTERS_'].keys()
    assert data['_MAP_DATASETS_TO_COUNTERS_']['jet/e'] == 'jet/njet'
    assert data["_MAP_DATASETS_TO_DATA_TYPES_"]['jet/e'] == float

    assert 'METpx' in data["_GROUPS_"]["_SINGLETONS_GROUP_"]
    assert data["_MAP_DATASETS_TO_COUNTERS_"]['METpx'] == "_SINGLETONS_GROUP_/COUNTER"
    assert data["_MAP_DATASETS_TO_DATA_TYPES_"]['METpx'] == int

    # check that we protect the protected names
    with pytest.raises(hepfile.errors.InputError):
        hepfile.create_dataset(
            data, '_META_', dtype=float)

    # check that datasets that are already in there don't get added again
    with pytest.warns(UserWarning):
        hepfile.create_dataset(
            data, 'e', group='jet', dtype=float, verbose=True)

    with pytest.warns(UserWarning):
        hepfile.create_dataset(data, 'METpx')

    # try with a group that doesn't exist yet
    with pytest.warns(UserWarning):
        hepfile.create_dataset(data, 'test_data', group='test_group')
    
################################################################################

def test_add_meta():
    # tests adding metadata to a group and dataset
    data = hepfile.initialize()
    hepfile.create_group(data, 'jet', counter='njet')
    hepfile.create_dataset(
        data, ['e', 'px', 'py', 'pz'], group='jet', dtype=float)
    hepfile.create_dataset(data, 'METpx', dtype=int, verbose=True)

    hepfile.add_meta(data, 'jet', 'This is one piece of data with units x')
    hepfile.add_meta(data, 'jet/e', 123)
    hepfile.add_meta(data, 'METpx', ['x', 'y', 'z'])

    assert 'jet' in data['_META_']
    assert 'jet/e' in data['_META_']
    assert 'METpx' in data['_META_']

    meta = data['_META_']
    assert meta['jet'] == 'This is one piece of data with units x'
    assert meta['jet/e'] == 123
    assert len(meta['METpx']) == 3

    # catch some warnings
    with pytest.warns(UserWarning):
        hepfile.add_meta(data, 'METpx', 1)
    
################################################################################
def test_write_file_metadata():

    filename = "FOR_TESTS.hdf5"
    with h5.File(filename, "r") as file:

        # Check default attribute existence
        assert 'date' in file.attrs.keys()
        assert 'hepfile_version' in file.attrs.keys()
        assert 'h5py_version' in file.attrs.keys()
        assert 'numpy_version' in file.attrs.keys()
        assert 'python_version' in file.attrs.keys()
        
        # Check default attributes are strings
        assert isinstance(file.attrs['date'], str)
        assert isinstance(file.attrs['hepfile_version'], str)
        assert isinstance(file.attrs['h5py_version'], str)
        assert isinstance(file.attrs['numpy_version'], str)
        assert isinstance(file.attrs['python_version'], str)

    # Adding a new attribute
    hepfile.write_file_metadata(filename, {'author': 'John Doe'}, verbose=True)
    with h5.File(filename, "r") as file:
        assert 'author' in file.attrs.keys()
        assert file.attrs['author'] == 'John Doe'

    # try not appending, just overwriting
    hepfile.write_file_metadata(filename, {'author': 'Jane Doe'},
                                append=False, write_default_values=False)
    with h5.File(filename, "r") as file:
        assert 'author' in file.attrs.keys()
        assert file.attrs['author'] == 'Jane Doe'        
        assert 'date' not in file.attrs.keys()
        assert 'hepfile_version' not in file.attrs.keys()
        
################################################################################

def test_write_file_header():

    filename = "FOR_TESTS.hdf5"

        # add some header information to the test file
    hdr = {'Author': 'Your Name',
       'Institution': 'Siena College',
           'Phone Number': 1234567890,
           'Other Info': [1, 2, 3]
           }
    hepfile.write_file_header(filename, hdr, verbose=True)

    # first test with return_type="dict"
    hdr_dict = hepfile.get_file_header(filename)

    assert 'Author' in hdr_dict.keys()
    assert 'Institution' in hdr_dict.keys()
    assert 'Phone Number' in hdr_dict.keys()

    assert hdr_dict['Author'] == 'Your Name'
    assert hdr_dict['Institution'] == 'Siena College'
    assert hdr_dict['Phone Number'] == '1234567890'
    assert len(hdr_dict['Other Info']) == 3

    # catch an error
    with pytest.raises(hepfile.errors.InputError):
        hepfile.write_file_header(filename, {})

################################################################################

def test_write_file():

    # load in the test file and modify that to rewrite it
    data, bucket = hepfile.load('FOR_TESTS.hdf5')

    hepfile.create_group(data, 'testing', counter='n_testing')
    hepfile.create_dataset(data, 'test', group='testing', dtype=str)

    bucket = hepfile.create_single_bucket(data)
    bucket['testing/test'].append('This is a test string')
    
    hepfile.pack(data, bucket)

    # test writing with some warnings
    with pytest.warns(UserWarning):
        hepfile.write_to_file('FOR_TESTS_OUTPUT.hdf5', data, verbose=True)

    with pytest.warns(UserWarning):
        hepfile.write_to_file('FOR_TESTS_OUTPUT.hdf5', data, force_single_precision=True)

    # test writing with metadata
    hepfile.add_meta(data, 'testing', 'This is just for testing')
    hepfile.add_meta(data, 'testing/test', 'This is just more for testing')

    with pytest.warns(UserWarning):
        hepfile.write_to_file('FOR_TESTS_OUTPUT.hdf5', data)

    with h5.File('FOR_TESTS_OUTPUT.hdf5', 'r') as f:

        assert f['testing'].attrs['meta'].decode() == 'This is just for testing'
        assert f['testing/test'].attrs['meta'].decode() == 'This is just more for testing'
