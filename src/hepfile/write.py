from __future__ import annotations

import numpy as np
import awkward as ak
import h5py as h5
import datetime
import sys
import hepfile


################################################################################
def initialize() -> dict:
    """ Creates an empty data dictionary

    Returns:

        data (dict): An empty data dictionary

    """

    data = {}
    data["_GROUPS_"] = {}
    data["_MAP_DATASETS_TO_COUNTERS_"] = {}
    data["_LIST_OF_COUNTERS_"] = []

    # For singleton entries, variables with only one entry per bucket.
    data["_GROUPS_"]["_SINGLETONS_GROUP_"] = ["COUNTER"]
    data["_MAP_DATASETS_TO_COUNTERS_"]["_SINGLETONS_GROUP_"] = "_SINGLETONS_GROUP_/COUNTER"
    data["_LIST_OF_COUNTERS_"].append("_SINGLETONS_GROUP_/COUNTER")

    data["_SINGLETONS_GROUP_/COUNTER"] = []
    data["_MAP_DATASETS_TO_DATA_TYPES_"] = {}
    data["_MAP_DATASETS_TO_DATA_TYPES_"]["_SINGLETONS_GROUP_/COUNTER"] = int

    data["_PROTECTED_NAMES_"] = ["_PROTECTED_NAMES_",
                                 "_GROUPS_",
                                 "_MAP_DATASETS_TO_COUNTERS_",
                                 "_MAP_DATASETS_TO_DATA_TYPES_"
                                 "_LIST_OF_COUNTERS_",
                                 "_SINGLETONS_GROUP_/COUNTER",
                                 ]

    return data


################################################################################
def clear_bucket(bucket:dict) -> None:
    """ Clears the data from the bucket dictionary - should the name of the function change?

    Args:
        bucket (dict): The dictionary to be cleared. This is designed to clear the data from
                      the lists in the bucket dictionary, but theoretically, it would
                      clear out the lists from any dictionary. 

    """

    for key in bucket.keys():

        if key == '_LIST_OF_COUNTERS_':
            continue

        if type(bucket[key]) == list:
            bucket[key].clear()
        elif type(bucket[key]) == int:
            if key in bucket['_LIST_OF_COUNTERS_']:
                bucket[key] = 0
            else:
                bucket[key] = -999
        elif type(bucket[key]) == float:
            bucket[key] = -999.0
        elif type(bucket[key]) == str:
            bucket[key] = "-999"


################################################################################
# Create a single bucket (dictionary) that will eventually be used to fill
# the overall dataset
################################################################################
def create_single_bucket(data:dict) -> dict:
    """ Creates an bucket dictionary that will be used to collect data and then
    packed into the the master data dictionary.

    Args:
        data (dict): Data dictionary that will hold all the data from the bucket.

    Returns:
        bucket (dict): The new bucket dictionary with keys and no bucket information

    """

    bucket = {}

    for k in data.keys():
        if k in data["_LIST_OF_COUNTERS_"]:
            bucket[k] = 0
        else:
            bucket[k] = data[k].copy()

    return bucket


################################################################################
# This adds a group in the dictionary, similar to
# a la CreateBranch in ROOT
################################################################################
def create_group(data:dict, group_name:str, counter:str=None):
    """ Adds a group in the dictionary

    Args:
        data (dict): Dictionary to which the group will be added

        group_name (string): Name of the group to be added

        counter (string): Name of the counter key. None by default

    """

    # Check for slashes in the group name. We can't have them.
    if group_name.find('/')>=0:
        new_group_name = group_name.replace('/','-')
        print("----------------------------------------------------")
        print(f"Slashes / are not allowed in group names")
        print(f"Replacing / with - in group name {group_name}")
        print(f"The new name will be {new_group_name}")
        print("----------------------------------------------------")
        group_name = new_group_name 

    # Change name of variable, just to keep code more understandable
    counter_name = counter

    # Create a counter_name if the user has not specified one
    if counter_name is None:
        print("----------------------------------------------------")
        print(
            f"There is no counter to go with group \033[1m{group_name}\033[0m")
        print("Are you sure that's what you want?")
        counter_name = f"N_{group_name}"
        print(f"Creating a counter called \033[1m{counter_name}\033[0m")
        print("-----------------------------------------------------")

    # Check for slashes in the counter name. We can't have them.
    if counter_name.find('/')>=0:
        new_counter_name = counter_name.replace('/','-')
        print("----------------------------------------------------")
        print(f"Slashes / are not allowed in counter names")
        print(f"Replacing / with - in counter name {counter_name}")
        print(f"The new name will be {new_counter_name}")
        print("----------------------------------------------------")
        counter_name = new_counter_name 

    keys = data.keys()

    # Then put the group and any datasets in there next.
    keyfound = False
    for k in keys:
        if group_name == k:
            print(f"\033[1m{group_name}\033[0m is already in the dictionary!")
            keyfound = True
            break

    if keyfound == False:

        data["_GROUPS_"][group_name] = []
        print(f"Adding group \033[1m{group_name}\033[0m")

        data["_GROUPS_"][group_name].append(counter_name)
        full_counter_name = f"{group_name}/{counter_name}"

        data["_MAP_DATASETS_TO_COUNTERS_"][group_name] = full_counter_name
        data["_MAP_DATASETS_TO_DATA_TYPES_"][full_counter_name] = int

        if full_counter_name not in data["_LIST_OF_COUNTERS_"]:
            data["_LIST_OF_COUNTERS_"].append(full_counter_name)

        data[full_counter_name] = []
        print(f"Adding a counter for \033[1m{group_name}\033[0m as \033[1m{counter_name}\033[0m")

    return 0

################################################################################

################################################################################
# This adds a dataset to the dictionary, similar to
# a la CreateBranch in ROOT
#
# This can also add a dataset that is not associate with a group
################################################################################
def create_dataset(data:dict, datasets:list, group:str=None, dtype:type=float):
    """ Adds a dataset to a group in a dictionary. If the group does not exist, it will be created.

    Args:
        data (dict): Dictionary that contains the group

        datasets (list): Dataset to be added to the group (This doesn't have to be a list)

        group (string): Name of group the dataset will be added to.  None by default

        dtype (type): The data type. None by default - I don't think this is every used 

    Returns:
        -1: If the group is None

    """

    if type(datasets) != list:
        datasets = [datasets]

    # Check for slashes in the group name. We can't have them.
    for i in range(len(datasets)):
        tempname = datasets[i]
        if tempname.find('/')>=0:
            new_dataset_name = tempname.replace('/','-')
            print("----------------------------------------------------")
            print(f"Slashes / are not allowed in dataset names")
            print(f"Replacing / with - in dataset name {tempname}")
            print(f"The new name will be {new_dataset_name}")
            print("----------------------------------------------------")
            datasets[i] = new_dataset_name 

    keys = data.keys()

    # These will be entries for the SINGLETON_GROUP, if there is no group passed in
    if group is None:

        for dataset in datasets:
            keyfound = False
            for k in data["_GROUPS_"]["_SINGLETONS_GROUP_"]:
                if dataset == k:
                    print(f"\033[1m{dataset}\033[0m is already in the dictionary!")
                    keyfound = True
            if keyfound == False:
                print(f"Adding dataset \033[1m{dataset}\033[0m to the dictionary as a SINGLETON.")
                data["_GROUPS_"]["_SINGLETONS_GROUP_"].append(dataset)
                data[dataset] = []
                data["_MAP_DATASETS_TO_COUNTERS_"][dataset] = "_SINGLETONS_GROUP_/COUNTER"

                data["_MAP_DATASETS_TO_DATA_TYPES_"][dataset] = dtype

        return 0

    # Put the counter in the dictionary first.
    keyfound = False
    for k in data["_GROUPS_"]:
        if group == k:
            keyfound = True

    # NEED TO FIX THIS PART SO THAT IT FINDS THE RIGHT COUNTER FROM THE GROUP
    if keyfound == False:
        print(f"Your group, \033[1m{group}\033[0m is not in the dictionary yet!")
        counter = f"N_{group}"
        print(f"Adding it, along with a counter of \033[1m{counter}\033[0m")
        create_group(data, group, counter=counter)

    # Then put the datasets into the group in there next.
    if type(datasets) != list:
        datasets = [datasets]

    for dataset in datasets:
        keyfound = False
        name = "%s/%s" % (group, dataset)
        for k in keys:
            if name == k:
                print(f"\033[1m{name}\033[0m is already in the dictionary!")
                keyfound = True
        if keyfound == False:
            print(f"Adding dataset \033[1m{dataset}\033[0m to the dictionary under group \033[1m{group}\033[0m.")
            data[name] = []
            data["_GROUPS_"][group].append(dataset)

            # Add a counter for this dataset for the group with which it is associated.
            counter = data["_MAP_DATASETS_TO_COUNTERS_"][group]
            # counter_name = "%s/%s" % (group,counter)
            data["_MAP_DATASETS_TO_COUNTERS_"][name] = counter

            data["_MAP_DATASETS_TO_DATA_TYPES_"][name] = dtype

    return 0


################################################################################
def pack(data:dict, bucket:dict, AUTO_SET_COUNTER:bool=True, EMPTY_OUT_BUCKET:bool=True, STRICT_CHECKING:bool=False, verbose:bool=False):
    """ Takes the data from an bucket and packs it into the data dictionary, 
    intelligently, so that it can be stored and extracted efficiently. 
    (This is analagous to the ROOT TTree::Fill() member function).

    Args:
        data (dict): Data dictionary to hold the entire dataset EDIT.

        bucket (dict): bucket to be packed into data.

        EMPTY_OUT_BUCKET (bool): If this is `True` then empty out the `bucket`
                                container in preparation for the next iteration. We used to ask the users to do
                                this "by hand" but now do it automatically by default. We allow the user to 
                                not do this, if they are running some sort of debugging. 

    """

    # Calculate the number of entries for each group and set the
    # value of that counter
    # This is all done in bucket
    if AUTO_SET_COUNTER:
        for group in data['_GROUPS_']:

            if verbose:
                print(f"group: {group}")

            datasets = data['_GROUPS_'][group]
            counter = data['_MAP_DATASETS_TO_COUNTERS_'][group]
            if counter == '_SINGLETONS_GROUP_/COUNTER':
                continue

            # Here we will calculate the values for the counters, based
            # on the size of the datasets
            counter_value = None

            # Loop over the datasets
            for d in datasets:
                full_dataset_name = group + "/" + d
                # Skip any counters
                if counter == full_dataset_name:
                    continue
                else:
                    # Grab the size of the first dataset
                    temp_counter_value = len(bucket[full_dataset_name])

                    # If we're not STRICT_CHECKING, then use that value for the
                    # counter and break the loop over the datasets, moving on
                    # to the next group.
                    if STRICT_CHECKING is False:
                        bucket[counter] = temp_counter_value
                        break
                    # Otherwise, we'll check that *all* the datasets have the same
                    # length.
                    else:
                        if counter_value is None:
                            counter_value = temp_counter_value
                            bucket[counter] = temp_counter_value
                        elif counter_value != temp_counter_value:
                            # In this case, we found two groups of different length!
                            # Print this to help the user identify their error
                            print(
                                f"Oh no!!!! Two datasets in group {group} have different sizes!")
                            for tempd in datasets:
                                temp_full_dataset_name = group + "/" + tempd
                                # Don't worry about the dataset
                                if counter == temp_full_dataset_name:
                                    continue
                                print(
                                    f"{tempd}: {len(bucket[temp_full_dataset_name])}")

                            # Return a value for the external program to catch.
                            return -1

    # Then pack the bucket into the data
    keys = list(bucket.keys())

    for key in keys:

        if (
            key == "_MAP_DATASETS_TO_COUNTERS_"
            or key == "_GROUPS_"
            or key == "_LIST_OF_COUNTERS_"
            or key == "_MAP_DATASETS_TO_DATA_TYPES_"
        ):
            continue

        # The singletons will only have 1 entry per bucket
        if key == "_SINGLETONS_GROUP_/COUNTER":
            data[key].append(1)
            continue

        if type(bucket[key]) == list:
            value = bucket[key]
            if len(value) > 0:
                data[key] += value
        else:
            # This is for counters and SINGLETONS
            if key in data["_GROUPS_"]["_SINGLETONS_GROUP_"]:
                if bucket[key] == None:
                    print(f"\n\033[1m{key}\033[0m is part of the SINGLETON group and is expected to have a value for each bucket.")
                    print("However it is None...exiting.\n")
                    exit()
                # Append the single value from the singletons
                else:
                    data[key].append(bucket[key])
            # Append the values to the counters
            else:
                data[key].append(bucket[key])

    # Clear out the bucket after it's been packed if that's what we want
    if EMPTY_OUT_BUCKET:
        clear_bucket(bucket)

    return 0

################################################################################


def _convert_list_and_key_to_string_data(datalist:list[any], key:str) -> str:
    """ Converts data dictionary to a string

    Args:
        datalist (list): A list to be saved as a string.

    Returns:
        key (string): We will assume that this will be unpacked as a dictionary,
                      and this will be the key for the list in that dictionary.

    """

    a = np.string_(key)

    mydataset = []
    b = np.string_("")
    nvals = len(datalist)
    for i, val in enumerate(datalist):
        b += np.string_(val)
        if i < nvals - 1:
            b += np.string_("__:__")
    mydataset.append([a, b])

    return mydataset


################################################################################

################################################################################
def _convert_dict_to_string_data(dictionary:dict) -> str:
    """ Converts data dictionary to a string

    Args:
        dictionary (dict): Dictionary to be converted to a string

    Returns:
        mydataset (string): String representation of the dataset

    """

    keys = dictionary.keys()

    nkeys = len(keys)

    mydataset = []
    for i, key in enumerate(keys):
        a = np.string_(key)
        b = np.string_(dictionary[key])
        mydataset.append([a, b])

    return mydataset


################################################################################
# This function writes default attributes and metadata to a file.
################################################################################
def write_file_metadata(filename:str, mydict:dict={}, write_default_values:bool=True, append:bool=True) -> h5.File:
    """ Writes file metadata in the attributes of an HDF5 file

    Args:
    filename (string): Name of output file

    mydict (dictionary): Metadata desired by user

    write_default_values (boolean): True if user wants to write/update the 
                                        default metadata: date, hepfile version, 
                                        h5py version, numpy version, and Python 
                                        version, false if otherwise.

    append (boolean): True if user wants to keep older metadata, false otherwise.

    Returns:
    hdoutfile (HDF5): File with new metadata

    """

    hdoutfile = h5.File(filename, "a")

    non_metadata = ["_NUMBER_OF_BUCKETS_"]

    if not append:
        for key in hdoutfile.attr.keys():
            if key not in non_metadata:
                del hdoutfile.attrs[key]

    if write_default_values:
        hdoutfile.attrs["date"] = datetime.datetime.now().isoformat(sep=" ")
        hdoutfile.attrs["hepfile_version"] = hepfile.__version__
        hdoutfile.attrs["numpy_version"] = np.__version__
        hdoutfile.attrs["h5py_version"] = h5.__version__
        hdoutfile.attrs["python_version"] = sys.version

    for key in mydict:
        hdoutfile.attrs[key] = mydict[key]

    hdoutfile.close()
    print("Metadata added")
    return hdoutfile


################################################################################

################################################################################
def write_to_file(
    filename:str, data:dict, comp_type:str=None, comp_opts:list=None, force_single_precision:bool=True,  verbose:bool=False
) -> h5.File:
    """ Writes the selected data to an HDF5 file

    Args:
        filename (string): Name of output file

        data (dictionary): Data to be written into output file

        comp_type (string): Type of compression

        force_single_precision (boolean): True if data should be written in single precision

    Returns:
        hdoutfile (HDF5): File to which the data has been written 

    """

    hdoutfile = h5.File(filename, "w")

    _GROUPS_ = data["_GROUPS_"].keys()

    # Convert this to a 2xN array for writing to the hdf5 file.
    # This gives us one small list of informtion if we need to pull out
    # small chunks of data
    mydataset = _convert_dict_to_string_data(data["_MAP_DATASETS_TO_COUNTERS_"])
    dset = hdoutfile.create_dataset(
        "_MAP_DATASETS_TO_COUNTERS_",
        data=mydataset,
        dtype="S256",
        compression=comp_type,
        compression_opts=comp_opts,
    )

    # Convert this to a 2xN array for writing to the hdf5 file.
    # This has the _GROUPS_ and the datasets in them.
    mydataset = _convert_list_and_key_to_string_data(
        data["_GROUPS_"]["_SINGLETONS_GROUP_"], "_SINGLETONSGROUPFORSTORAGE_"
    )
    dset = hdoutfile.create_dataset(
        "_SINGLETONSGROUPFORSTORAGE_",
        data=mydataset,
        dtype="S256",
        compression=comp_type,
        compression_opts=comp_opts,
    )

    print(data['_MAP_DATASETS_TO_DATA_TYPES_'])

    for group in _GROUPS_:

        hdoutfile.create_group(group)
        hdoutfile[group].attrs["counter"] = np.string_(
            data["_MAP_DATASETS_TO_COUNTERS_"][group]
        )

        datasets = data["_GROUPS_"][group]
        
        for dataset in datasets:

            name = None
            if group == "_SINGLETONS_GROUP_" and dataset is not "COUNTER":
                name = dataset
            else:
                name = "%s/%s" % (group, dataset)

            if verbose is True:
                print(f"Writing {name} to file")

            x = data[name]

            dataset_dtype = data['_MAP_DATASETS_TO_DATA_TYPES_'][name]
            
            if type(x) == list:
                if verbose is True:
                    print("\tConverting list to array...")
                x = np.array(x)

            # Do single precision only, unless specified
            if force_single_precision == True:

                # different type calls depending on input datastructure
                if isinstance(x, np.ndarray):
                    dtype = x.dtype
                elif isinstance(x, ak.Array) or isinstance(x, ak.Record):
                    dtype = x.type
                else:
                    dtype = None
                    raise Warning('Not a proper data type to convert to single precision, skipping!')
                
                if dtype == np.float64:
                    if verbose is True:
                        print("\tConverting array to single precision...")
                    x = x.astype(np.float32)
                    dataset_dtype = np.float32

            if dataset_dtype is not str:

                if verbose is True:
                    print("\tWriting to file...")

                hdoutfile.create_dataset(
                    name, data=x, compression=comp_type, compression_opts=comp_opts, dtype=dataset_dtype
                )
            else:
                # For writing strings, we need to make sure our strings are ascii and not Unicode
                #
                # See my question on StackOverflow and the super-helpful response!
                #
                # https://stackoverflow.com/questions/68500454/can-i-use-h5py-to-write-strings-to-an-hdf5-file-in-one-line-rather-than-looping
                dataset_dtype = h5.special_dtype(vlen=str)
                longest_word = len(max(x, key=len))
                arr = np.array(x, dtype='S'+str(longest_word))
                hdoutfile.create_dataset(
                    name, data=arr, dtype=dataset_dtype,  compression=comp_type, compression_opts=comp_opts)

            if (verbose):
                print(f"Writing to file {name} as type {str(dataset_dtype)}")

    # Get the number of buckets
    counters = data["_LIST_OF_COUNTERS_"]
    _NUMBER_OF_BUCKETS_ = -1
    prevcounter = None
    for i, countername in enumerate(counters):
        ncounter = len(data[countername])
        #print("%-32s has %-12d entries" % (countername, ncounter))
        print(f"{countername:<32s} has {ncounter:<12d} entries")
        if i > 0 and ncounter != _NUMBER_OF_BUCKETS_:
            print("-------- WARNING -----------")
            print(f"{countername} and {prevcounter} have differing numbers of entries!")
            print("-------- WARNING -----------")
            # SHOULD WE EXIT ON THIS?

        if _NUMBER_OF_BUCKETS_ < ncounter:
            _NUMBER_OF_BUCKETS_ = ncounter

        prevcounter = countername

    hdoutfile.attrs["_NUMBER_OF_BUCKETS_"] = _NUMBER_OF_BUCKETS_
    hdoutfile.close()

    write_file_metadata(filename)

    return hdoutfile
