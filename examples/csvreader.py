import numpy as np
import hepfile as hep


def sep_cols_data_ids(filename):

    #with open(filename) as input:
    #    cols = input.read().split('\n', 1)[0].split(",")[1:]

    #data = np.loadtxt(filename, unpack=True, dtype=str,
    #                  delimiter=",", skiprows=1)
    #data_ID = data[0].astype(np.int32)
    #data = data[1:]
    data = np.loadtxt(filename, unpack=True, dtype=str,
                     delimiter=",", comments = '$')

    data_ID = data[0][1:].astype(np.int32)
    cols = data[1:, 0].tolist()
    data = data[1:, 1:]
    return cols, data, data_ID


def setup_group(data, groupname, counter, datasets):
    hep.create_group(data, groupname=groupname, counter=counter)
    #for dset in datasets:
    hep.create_dataset(data, datasets, group=groupname, dtype = str)


def fill_event_group(event, i, groupname, cols, counters, data):
    for j in range(len(counters)):
        if counters[j] == i:
            event[f'{groupname}/ID'] += 1
            for k in range(len(cols)):
                event[f'{groupname}/{cols[k]}'].append(data[k][j])


p_cols, p_data, p_ID = sep_cols_data_ids('sheet1.csv')
v_cols, v_data, v_ID = sep_cols_data_ids('sheet2.csv')
h_cols, h_data, h_ID = sep_cols_data_ids('sheet3.csv')

min_ID = min(min(p_ID), min(v_ID), min(h_ID))
max_ID = max(max(p_ID), max(v_ID), max(h_ID))

town = hep.initialize()
setup_group(town, 'people', 'ID', p_cols)
setup_group(town, 'vehicles', 'ID', v_cols)
setup_group(town, 'houses', 'ID', h_cols)
bucket = hep.create_single_bucket(town)



for i in range(min_ID, max_ID+1):
    fill_event_group(bucket, i, 'people', p_cols, p_ID, p_data)
    fill_event_group(bucket, i, 'vehicles', v_cols, v_ID, v_data)
    fill_event_group(bucket, i, 'houses', h_cols, h_ID, h_data)
    hep.pack(town, bucket)
    hep.clear_event(bucket)

hep.write_to_file("town_hep.hdf5", town, force_single_precision=False)
