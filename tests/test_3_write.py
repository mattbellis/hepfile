import numpy as np
import hepfile
import h5py as h5

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

    hepfile.create_group(data,"test/slash",counter='ntest/slash')

    assert 'test-slash' in data['_GROUPS_']
    assert 'test-slash/ntest-slash' in data.keys()

################################################################################

################################################################################


def test_pack():

    data = hepfile.initialize()
    hepfile.create_group(data, 'obj', counter='nobj')
    hepfile.create_dataset(data, ['myfloat'], group='obj', dtype=float)
    hepfile.create_dataset(data, ['myint'], group='obj', dtype=int)
    hepfile.create_dataset(data, ['mystr'], group='obj', dtype=str)

    bucket = hepfile.create_single_bucket(data)

    # Normal packing test

    for i in range(5):
        bucket['obj/myfloat'].append(2.0)
        bucket['obj/myint'].append(2)
        bucket['obj/mystr'].append('two')
    bucket['obj/nobj'] = 5

    test = hepfile.pack(data, bucket)
    assert test == 0
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

    # Is the mistake propagated?
    bucket['obj/nobj'] = 2

    hepfile.pack(data, bucket, AUTO_SET_COUNTER=False)
    assert data['obj/nobj'][1] == 2

    # Fix mistake
    data['obj/nobj'][1] = 2

    # STRICT_CHECKING = True
    bucket['obj/myfloat'].append(2.0)
    bucket['obj/myint'].append(2)
    # 1 != 0, strict checking should fail.

    try:
        test = hepfile.pack(data, bucket, STRICT_CHECKING=True)
    except hepfile.errors.DatasetSizeDiscrepancy:
        pass
    else:
        assert test == -1
        # Was nothing packed?
        assert len(data['obj/myint']) == 6
        # Is bucket not cleared?
        assert isEmpty(bucket) == False
        
    # EMPTY_OUT_BUCKET = False

    bucket['obj/mystr'].append('two')

    hepfile.pack(data, bucket, EMPTY_OUT_BUCKET=False)

    assert isEmpty(bucket) == False

    #assert type(data['obj/mystr'][0]) is str


################################################################################


################################################################################
def test_create_dataset():

    data = hepfile.initialize()
    hepfile.create_group(data, 'jet', counter='njet')
    hepfile.create_dataset(
        data, ['e', 'px', 'py', 'pz'], group='jet', dtype=float)
    hepfile.create_dataset(data, 'METpx', dtype=int)

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
################################################################################


################################################################################
def test_write_file_metadata():

    filename = "FOR_TESTS.hdf5"
    file = h5.File(filename, "r")

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

    file.close()

    # Adding a new attribute
    hepfile.write_file_metadata(filename, {'author': 'John Doe'})
    file = h5.File(filename, "r")

    assert 'author' in file.attrs.keys()
    assert file.attrs['author'] == 'John Doe'

    file.close()
################################################################################
