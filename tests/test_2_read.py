import numpy as np
import h5py as h5
import hepfile

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

    # Test for poor uses of subset
    test_data, test_bucket = hepfile.load(
        filename, False, desired_datasets, [0,0])
    
    assert len(test_data['_LIST_OF_DATASETS_']) == 0
    assert len(test_bucket.keys()) == 0

    test_data, test_bucket = hepfile.load(
        filename, False, desired_datasets, [10,0])
    
    assert len(test_data['_LIST_OF_DATASETS_']) == 0
    assert len(test_bucket.keys()) == 0

    test_data, test_bucket = hepfile.load(
        filename, False, desired_datasets, subset=0)
    
    assert len(test_data['_LIST_OF_DATASETS_']) == 0
    assert len(test_bucket.keys()) == 0

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
