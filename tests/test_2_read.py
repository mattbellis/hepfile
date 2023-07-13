import numpy as np
import h5py as h5
import hepfile
import pytest

import time

#import sys
# sys.path.append('./scripts')
#from write_h5hep_file_for_unit_tests import write_h5hep_file_for_unit_tests

from write_file_for_unit_tests import write_file_for_unit_tests


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


def test_load():

    write_file_for_unit_tests()

    # This assumes you run nosetests from the h5hep directory and not
    # the tests directory.
    filename = "FOR_TESTS.hdf5"
    desired_datasets = ['jet', 'muon']
    subset = 5

    test_data, test_bucket = hepfile.load(
        filename, False, desired_datasets, subset)

    assert isinstance(test_data, dict)
    assert isinstance(test_bucket, dict)

    assert isEmpty(test_bucket) == True
    assert isEmpty(test_data) == False

    # Testing desired_datasets
    assert "jet/e" in test_data.keys()
    assert "jet/e" in test_data.keys()
    assert "METpx" not in test_data.keys()
    assert "METpx" not in test_data.keys()

    # Testing subsets
    assert len(test_data["jet/njet"]) == 5

    with pytest.warns(UserWarning):
        test_data, test_bucket = hepfile.load(
            filename, False, desired_datasets, 1000)

    assert len(test_data["jet/njet"]) == 10

    # Passing in a range of subsets
    subset = (0,4)
    test_data, test_bucket = hepfile.load(
        filename, False, desired_datasets, subset=subset)
    assert len(test_data["jet/njet"]) == 4

    subset = (1,5)
    test_data, test_bucket = hepfile.load(
        filename, False, desired_datasets, subset=subset)
    assert len(test_data["jet/njet"]) == 4

    subset = [1,5]
    test_data, test_bucket = hepfile.load(
        filename, False, desired_datasets, subset=subset)
    assert len(test_data["jet/njet"]) == 4

    # test desired_groups as a string
    test_data, test_bucket = hepfile.load(
        filename, False, desired_groups='jet', subset=subset)
    assert len(test_data["jet/njet"]) == 4
    
    # Test for poor uses of subset
    with pytest.raises(hepfile.errors.RangeSubsetError):
        test_data, test_bucket = hepfile.load(
            filename, False, desired_datasets, [0,0])

    with pytest.raises(hepfile.errors.RangeSubsetError):
        test_data, test_bucket = hepfile.load(
            filename, False, desired_datasets, [10,0])

    with pytest.raises(hepfile.errors.RangeSubsetError):
        test_data, test_bucket = hepfile.load(
            filename, False, desired_datasets, subset=0)

    with pytest.raises(hepfile.errors.RangeSubsetError):
        test_data, test_bucket = hepfile.load(
            filename, False, desired_datasets, subset=(int(1e10), int(1e11)))

    # test different return types
    # this should throw an error
    with pytest.raises(hepfile.errors.InputError):
        test_data, test_bucket = hepfile.load(
            filename, verbose=False, desired_groups=desired_datasets, return_type='foo'
            )

    # now with return_type='awkward'
    awk, bucket = hepfile.load(
        filename, return_type='awkward'
    )

    assert 'jet' in awk.fields
    assert 'muons' in awk.fields
    assert 'METpx' in awk.fields
    assert 'METpy' in awk.fields

    # and with return_type='pandas'
    dfs, bucket = hepfile.load(
        filename, return_type='pandas'
        )
    
    for k in ('_SINGLETONS_GROUP_', 'jet'):
        assert k in dfs.keys()
        assert 'event_num' in dfs[k]

    jet = dfs['jet']
    assert len(jet.e[jet.event_num == 0]) == 5

    # check that with verbose flags we get warnings
    with pytest.warns(UserWarning):
        test_data, test_bucket = hepfile.load(
            filename, True, desired_datasets, subset=int(1e10))
    
def test_unpack():

    # This assumes you run nosetests from the h5hep directory and not
    # the tests directory.
    filename = "FOR_TESTS.hdf5"
    desired_datasets = ['jet', 'muon']
    subset = 10

    bucket, data = hepfile.load(filename, False, desired_datasets, subset)

    hepfile.unpack(data, bucket)

    assert isEmpty(bucket) == False


def test_get_nbuckets_in_file():

    # This assumes you run nosetests from the h5hep directory and not
    # the tests directory.
    filename = "FOR_TESTS.hdf5"
    
    nbuckets = hepfile.get_nbuckets_in_file(filename)

    assert nbuckets == 10

    # test that incorrect inputs throw custom errors
    with pytest.raises(hepfile.errors.InputError):
        nbuckets = hepfile.get_nbuckets_in_file(1)

def test_get_nbuckets_in_data():

    data, bucket = hepfile.load("FOR_TESTS.hdf5")
    nbuckets = hepfile.get_nbuckets_in_data(data)
    assert nbuckets == 10

    # test incorrect input
    with pytest.raises(hepfile.errors.InputError):
        nbuckets = hepfile.get_nbuckets_in_data([])

    # test missing key in data dictionary
    del data['_NUMBER_OF_BUCKETS_']
    with pytest.raises(AttributeError):
        nbuckets = hepfile.get_nbuckets_in_data(data)
        
def test_get_file_metadata():

    filename = "FOR_TESTS.hdf5"
    metadata = hepfile.get_file_metadata(filename)

    assert 'date' in metadata
    assert 'hepfile_version' in metadata
    assert 'h5py_version' in metadata
    assert 'numpy_version' in metadata
    assert 'python_version' in metadata

    # Check default attributes are strings
    assert isinstance(metadata['date'], str)
    assert isinstance(metadata['hepfile_version'], str)
    assert isinstance(metadata['h5py_version'], str)
    assert isinstance(metadata['numpy_version'], str)
    assert isinstance(metadata['python_version'], str)

    # just test printing the file metadata to make sure it runs
    meta = hepfile.print_file_metadata(filename)

    # new file with no metadata and check some errors
    newfile = 'FOR_TESTS_NO_META.h5'
    with h5.File(filename, 'r') as f1:
        with h5.File(newfile, 'w') as f2:
            for d in f1:
                f1.copy(d, f2)

    with pytest.raises(hepfile.errors.MetadataNotFound):
        metadata = hepfile.get_file_metadata(newfile)

    with pytest.warns(UserWarning):
        meta = hepfile.print_file_metadata(newfile)

    with pytest.raises(AttributeError):
        hepfile.get_nbuckets_in_file(newfile)
    
    # add some other attributes and test with those
    with h5.File(filename, 'r+') as f:
        f.attrs['new_data'] = 1

    meta = hepfile.get_file_metadata(filename)
    hepfile.print_file_metadata(filename)
    
    
def test_get_file_header():


    filename = "FOR_TESTS.hdf5"

    # before we add the header check if it throws an error
    with pytest.raises(hepfile.errors.HeaderNotFound):
        h = hepfile.get_file_header(filename)
        
    # add some header information to the test file
    hdr = {'Author': 'Your Name',
       'Institution': 'Siena College',
       'Phone Number': 1234567890}
    hepfile.write_file_header(filename, hdr)

    # first test with return_type="dict"
    hdr_dict = hepfile.get_file_header(filename)

    assert 'Author' in hdr_dict.keys()
    assert 'Institution' in hdr_dict.keys()
    assert 'Phone Number' in hdr_dict.keys()

    assert hdr_dict['Author'] == 'Your Name'
    assert hdr_dict['Institution'] == 'Siena College'
    assert hdr_dict['Phone Number'] == '1234567890'

    # test with return_type='df'
    hdr_df = hepfile.get_file_header(filename, return_type='df')

    assert 'Author' in hdr_df.columns
    assert 'Institution' in hdr_df.columns
    assert 'Phone Number' in hdr_df.columns

    assert hdr_df['Author'].iloc[0] == 'Your Name'
    assert hdr_df['Institution'].iloc[0] == 'Siena College'
    assert hdr_df['Phone Number'].iloc[0] == '1234567890'

    
    # test with return_type='dataframe'
    hdr_df = hepfile.get_file_header(filename, return_type='dataframe')

    assert 'Author' in hdr_df.columns
    assert 'Institution' in hdr_df.columns
    assert 'Phone Number' in hdr_df.columns

    assert hdr_df['Author'].iloc[0] == 'Your Name'
    assert hdr_df['Institution'].iloc[0] == 'Siena College'
    assert hdr_df['Phone Number'].iloc[0] == '1234567890'
    
    # test other common errors
    with pytest.raises(hepfile.errors.InputError):
        hepfile.get_file_header(filename, return_type=0)

    # just test printing the file header to make sure it runs
    hdr = hepfile.print_file_header(filename)
