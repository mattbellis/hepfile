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

def test_initialize():

    test_data = hepfile.initialize()

    assert isinstance(test_data, dict)
    assert test_data['groups']['_SINGLETON_'] ==  ['INDEX']
    assert test_data['datasets_and_counters']['_SINGLETON_'] == '_SINGLETON_/INDEX'
    assert test_data['list_of_counters'] == ['_SINGLETON_/INDEX']
    assert test_data['_SINGLETON_/INDEX'] == []


def test_clear_event():
	
    # This assumes you run nosetests from the h5hep directory and not 
    # the tests directory.
    filename = "./test_data/FOR_TESTS.hdf5"
    desired_datasets = ['jet','muon']
    subset = 1000

    data, event = hepfile.load(filename, False, desired_datasets, subset)

    hepfile.clear_event(event)

    assert isEmpty(event) == True

def test_create_single_event():

    data = hepfile.initialize()

    hepfile.create_group(data,'jet',counter='njet')
    hepfile.create_dataset(data,['e','px','py','pz'],group='jet',dtype=float)

    hepfile.create_group(data,'muons',counter='nmuon')
    hepfile.create_dataset(data,['e','px','py','pz'],group='muons',dtype=float)

    test_event = hepfile.create_single_event(data)

    assert isEmpty(test_event) == False
    assert isinstance(test_event, dict)

def test_create_group():

    data = hepfile.initialize()
    hepfile.create_group(data,'jet',counter='njet')

    assert isEmpty(data['groups']) == False
    assert 'jet/njet' in data.keys()


def test_create_dataset():

    data = hepfile.initialize()
    hepfile.create_group(data,'jet',counter='njet')
    hepfile.create_dataset(data,['e','px','py','pz'],group='jet',dtype=float)


    assert isEmpty(data['groups']) == False
    assert 'jet/njet' in data.keys()
    assert 'jet/e' in data.keys()
    assert 'jet/px' in data.keys()
    assert 'jet/e' in data['datasets_and_counters'].keys()
    assert data['datasets_and_counters']['jet/e'] == 'jet/njet'


def test_write_file_metadata():

    ##### NEED TO WRITE THIS #####
    assert 1==1








