import numpy as np
import h5py as h5
import hepfile 

import time

import sys
sys.path.append('./scripts')
#from write_h5hep_file_for_unit_tests import write_h5hep_file_for_unit_tests

def isEmpty(dictionary):
    test = True
    print(dictionary.keys())
    for key in dictionary.keys():
        print(key)
        print(dictionary[key])
        print(type(dictionary[key]))
        if dictionary[key] is None:
            test = True
        elif type(dictionary[key])==list or type(dictionary[key])==np.ndarray:
            if len(dictionary[key]) > 0:
                test = False

    return test


def test_load():

    #write_h5hep_file_for_unit_tests()

    # This assumes you run nosetests from the h5hep directory and not 
    # the tests directory.
    filename = "FOR_TESTS.hdf5"
    desired_datasets = ['jet','muon']
    subset = 1000

    test_data,test_event = hepfile.load(filename, False, desired_datasets, subset)

    assert isinstance(test_data, dict)
    assert isinstance(test_event, dict)

    assert isEmpty(test_event) == True
    assert isEmpty(test_data) == False

def test_unpack():
	
    # This assumes you run nosetests from the h5hep directory and not 
    # the tests directory.
    filename = "FOR_TESTS.hdf5"
    desired_datasets = ['jet','muon']
    subset = 1000

    event, data = hepfile.load(filename, False, desired_datasets, subset)

    hepfile.unpack(data, event)

    assert isEmpty(event) == False


def test_get_nentries():
	
    # This assumes you run nosetests from the h5hep directory and not 
    # the tests directory.
    filename = "FOR_TESTS.hdf5"

    nentries = hepfile.get_nentries(filename)

    assert nentries == 10

def test_get_file_metadata():

    filename = "FOR_TESTS.hdf5"

    metadata = hepfile.get_file_metadata(filename)

    assert 'date' in metadata
    assert 'hepfile_version' in metadata
    assert 'h5py_version' in metadata
    assert 'numpy_version' in metadata
    assert 'python_version' in metadata

    #Check default attributes are strings
    assert isinstance(metadata['date'],str)
    assert isinstance(metadata['hepfile_version'],str)
    assert isinstance(metadata['h5py_version'],str)
    assert isinstance(metadata['numpy_version'],str)
    assert isinstance(metadata['python_version'],str)





