import hepfile as hf
import awkward as ak
import numpy as np

def test_dictlike_to_hepfile():
    '''
    Unit tests for hepfile.dict_tools.dictlike_to_hepfile
    '''

    # test dictionary
    d = [
        {
            'jet': {
                'px': [1,2,3],
                'py': [1,2,3]
            },
            'muons': {
                'px': [1,2,3],
                'py': [1,2,3]
            },
            'other': 'this'
        },
        {
            'jet': {
                'px': [3,4,6,7],
                'py': [3,4,6,7]
            },
            'muons': {
                'px': [3,4,6,7],
                'py': [3,4,6,7],
            },
            'other': 'this'
        }
    ]

    
    out = 'test.hdf5'
    ak_dict = hf.dict_tools.dictlike_to_hepfile(d, out, how_to_pack='awkward')

    # some tests to check the keys
    for key in ak_dict.fields:
        assert key in d[0].keys()
    
    # some tests to check the data integrity
    test1 = d[0]['jet']['px'] + d[1]['jet']['px']
    assert ak.all(ak.flatten(ak_dict.jet.px) == test1)

    test2 = d[0]['muons']['py'] + d[1]['muons']['py']
    assert ak.all(ak.flatten(ak_dict.muons.py) == test2)

    test3 = ['this', 'this']
    assert ak.all(ak_dict.other == test3)

def test_dict_append():
    '''
    Unit tests for hepfile.dict_tools.append
    '''

    # original test dictionary
    d = [
        {
            'jet': {
                'px': [1,2,3],
                'py': [1,2,3]
            },
            'muons': {
                'px': [1,2,3],
                'py': [1,2,3]
            },
            'other': 'this'
        },
        {
            'jet': {
                'px': [3,4,6,7],
                'py': [3,4,6,7]
            },
            'muons': {
                'px': [3,4,6,7],
                'py': [3,4,6,7],
            },
            'other': 'this'
        }
    ]


    # convert to an awkward array
    out = 'test.hdf5'
    ak_dict = hf.dict_tools.dictlike_to_hepfile(d, out, write_hepfile=False, how_to_pack='awkward')

    # dictionary of data to append
    new_dict = {'jet': {'px': [10, 100], 'py': [0, 0]},
                'muons': {'px': [5, 1000], 'py': [0, -1]},
                'other': 2
                }
    print(ak_dict, new_dict)
    mod = hf.dict_tools.append(ak_dict, new_dict)

    # some tests to check the keys
    for key in ak_dict.fields:
        assert key in d[0].keys()

    # check data
    test1 = d[0]['jet']['px'] + d[1]['jet']['px'] + new_dict['jet']['px']
    assert ak.all(ak.flatten(mod.jet.px) == test1)

    test2 = d[0]['muons']['py'] + d[1]['muons']['py'] + new_dict['muons']['py']
    assert ak.all(ak.flatten(mod.muons.py) == test2)

    test3 = ['this', 'this', 2]
    assert np.all(np.array(ak.to_list(mod.other)) == test3)
