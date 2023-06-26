"""
Functions to assist in writing a hepfile "from scratch"
"""

from __future__ import annotations

import datetime
import sys
import warnings

import numpy as np
import awkward as ak
import h5py as h5

import hepfile
from . import constants
from .errors import InputError, DatasetSizeDiscrepancy, MissingSingletonValue


################################################################################
def initialize() -> dict:
    """Creates an empty data dictionary

    Returns:

        data (dict): An empty data dictionary

    """

    data = {}
    data["_GROUPS_"] = {}
    data["_MAP_DATASETS_TO_COUNTERS_"] = {}
    data["_LIST_OF_COUNTERS_"] = []

    # For singleton entries, variables with only one entry per bucket.
    data["_GROUPS_"]["_SINGLETONS_GROUP_"] = ["COUNTER"]
    data["_MAP_DATASETS_TO_COUNTERS_"][
        "_SINGLETONS_GROUP_"
    ] = "_SINGLETONS_GROUP_/COUNTER"
    data["_LIST_OF_COUNTERS_"].append("_SINGLETONS_GROUP_/COUNTER")

    data["_SINGLETONS_GROUP_/COUNTER"] = []
    data["_MAP_DATASETS_TO_DATA_TYPES_"] = {}
    data["_MAP_DATASETS_TO_DATA_TYPES_"]["_SINGLETONS_GROUP_/COUNTER"] = int

    data["_META_"] = {}

    return data


################################################################################
def clear_bucket(bucket: dict) -> None:
    """Clears the data from the bucket dictionary - should the name of the function change?

    Args:
        bucket (dict): The dictionary to be cleared. This is designed to clear the data from
                      the lists in the bucket dictionary, but theoretically, it would
                      clear out the lists from any dictionary.

    """

    for key in bucket.keys():
        if key == "_LIST_OF_COUNTERS_":
            continue

        if isinstance(bucket[key], list):
            bucket[key].clear()
        elif isinstance(bucket[key], int):
            if key in bucket["_LIST_OF_COUNTERS_"]:
                bucket[key] = 0
            else:
                bucket[key] = -999
        elif isinstance(bucket[key], float):
            bucket[key] = -999.0
        elif isinstance(bucket[key], str):
            bucket[key] = "-999"


################################################################################
# Create a single bucket (dictionary) that will eventually be used to fill
# the overall dataset
################################################################################
def create_single_bucket(data: dict) -> dict:
    """Creates an bucket dictionary that will be used to collect data and then
    packed into the the master data dictionary.

    Args:
        data (dict): Data dictionary that will hold all the data from the bucket.

    Returns:
        bucket (dict): The new bucket dictionary with keys and no bucket information

    """

    bucket = {k: data[k].copy() for k in data.keys()}
    for k in bucket["_LIST_OF_COUNTERS_"]:
        bucket[k] = 0

    return bucket


################################################################################
# This adds a group in the dictionary, similar to
# a la CreateBranch in ROOT
################################################################################
def create_group(data: dict, group_name: str, counter: str = None, verbose=False):
    """Adds a group in the dictionary

    Args:
        data (dict): Dictionary to which the group will be added

        group_name (string): Name of the group to be added

        counter (string): Name of the counter key. None by default

    """
    # check that group_name isn't in protected_names
    if group_name in constants.protected_names:
        raise InputError(
            f"{group_name} is protected, please choose a different group name!"
        )

    # Check for slashes in the group name. We can't have them.
    if "/" in group_name:
        new_group_name = group_name.replace("/", "-")
        print("----------------------------------------------------")
        print("Slashes / are not allowed in group names")
        print(f"Replacing / with - in group name {group_name}")
        print(f"The new name will be {new_group_name}")
        print("----------------------------------------------------")
        group_name = new_group_name

    # Change name of variable, just to keep code more understandable
    counter_name = counter

    # Create a counter_name if the user has not specified one
    if counter_name is None:
        print("----------------------------------------------------")
        print(f"There is no counter to go with group \033[1m{group_name}\033[0m")
        print("Are you sure that's what you want?")
        counter_name = f"N_{group_name}"
        print(f"Creating a counter called \033[1m{counter_name}\033[0m")
        print("-----------------------------------------------------")

    # Check for slashes in the counter name. We can't have them.
    if "/" in counter_name:
        new_counter_name = counter_name.replace("/", "-")
        print("----------------------------------------------------")
        print("Slashes / are not allowed in counter names")
        print(f"Replacing / with - in counter name {counter_name}")
        print(f"The new name will be {new_counter_name}")
        print("----------------------------------------------------")
        counter_name = new_counter_name

    keys = data.keys()

    # Then put the group and any datasets in there next.
    keyfound = False
    if group_name in keys:
        print(f"\033[1m{group_name}\033[0m is already in the dictionary!")
        keyfound = True

    if not keyfound:
        data["_GROUPS_"][group_name] = []
        if verbose:
            print(f"Adding group \033[1m{group_name}\033[0m")

        data["_GROUPS_"][group_name].append(counter_name)
        full_counter_name = f"{group_name}/{counter_name}"

        data["_MAP_DATASETS_TO_COUNTERS_"][group_name] = full_counter_name
        data["_MAP_DATASETS_TO_DATA_TYPES_"][full_counter_name] = int

        if full_counter_name not in data["_LIST_OF_COUNTERS_"]:
            data["_LIST_OF_COUNTERS_"].append(full_counter_name)

        data[full_counter_name] = []
        if verbose:
            print(
                f"Adding a counter for \033[1m{group_name}\033[0m as \033[1m{counter_name}\033[0m"
            )

    return 0


################################################################################


################################################################################
# This adds a dataset to the dictionary, similar to
# a la CreateBranch in ROOT
#
# This can also add a dataset that is not associate with a group
################################################################################
def create_dataset(
    data: dict, datasets: list, group: str = None, dtype: type = float, verbose=False
):
    """Adds a dataset to a group in a dictionary. If the group does not exist, it will be created.

    Args:
        data (dict): Dictionary that contains the group

        datasets (list): Dataset to be added to the group (This doesn't have to be a list)

        group (string): Name of group the dataset will be added to.  None by default

        dtype (type): The data type. None by default - I don't think this is every used

    Returns:
        -1: If the group is None

    """

    if not isinstance(datasets, list):
        datasets = [datasets]

    # Check for slashes in the dataset name. We can't have them.
    for i, tempname in enumerate(datasets):
        # check that tempname isn't in protected_names
        if tempname in constants.protected_names:
            raise InputError(
                f"{tempname} is protected, please choose a different dataset name!"
            )

        if "/" in tempname:
            new_dataset_name = tempname.replace("/", "-")
            print("----------------------------------------------------")
            print("Slashes / are not allowed in dataset names")
            print(f"Replacing / with - in dataset name {tempname}")
            print(f"The new name will be {new_dataset_name}")
            print("----------------------------------------------------")
            datasets[i] = new_dataset_name

    keys = data.keys()

    # These will be entries for the SINGLETON_GROUP, if there is no group passed in
    if group is None:
        for dataset in datasets:
            keyfound = False

            if dataset in data["_GROUPS_"]["_SINGLETONS_GROUP_"]:
                print(f"\033[1m{dataset}\033[0m is already in the dictionary!")
                keyfound = True

            if not keyfound:
                if verbose:
                    print(
                        f"Adding dataset \033[1m{dataset}\033[0m to the dictionary as a SINGLETON."
                    )
                data["_GROUPS_"]["_SINGLETONS_GROUP_"].append(dataset)
                data[dataset] = []
                data["_MAP_DATASETS_TO_COUNTERS_"][
                    dataset
                ] = "_SINGLETONS_GROUP_/COUNTER"

                data["_MAP_DATASETS_TO_DATA_TYPES_"][dataset] = dtype

        return 0

    # Put the counter in the dictionary first.
    keyfound = group in data["_GROUPS_"]

    # NEED TO FIX THIS PART SO THAT IT FINDS THE RIGHT COUNTER FROM THE GROUP
    if not keyfound:
        counter = f"N_{group}"
        warnings.warn(
            f"Your group, \033[1m{group}\033[0m is not in the dictionary yet! \
            Adding it, along with a counter of \033[1m{counter}\033[0m"
        )
        create_group(data, group, counter=counter)

    for dataset in datasets:
        keyfound = False
        name = f"{group}/{dataset}"

        # check that tempname isn't in protected_names
        if name in constants.protected_names:
            raise InputError(
                f"{name} is protected, please choose a different dataset or group name!"
            )

        if name in keys:
            warnings.warn(
                f"\033[1m{name}\033[0m is already in the dictionary! Skipping!!!"
            )
            keyfound = True

        if not keyfound:
            if verbose:
                print(
                    f"Adding dataset \033[1m{dataset}\033[0m to the dictionary \
                    under group \033[1m{group}\033[0m."
                )
            data[name] = []
            data["_GROUPS_"][group].append(dataset)

            # Add a counter for this dataset for the group with which it is associated.
            counter = data["_MAP_DATASETS_TO_COUNTERS_"][group]
            # counter_name = "%s/%s" % (group,counter)
            data["_MAP_DATASETS_TO_COUNTERS_"][name] = counter

            data["_MAP_DATASETS_TO_DATA_TYPES_"][name] = dtype

    return 0


###############################################################################
def add_meta(data: dict, name: str, meta_data: list):
    """
    Create metadata for a group (or singleton) and add it to data

    Args:
        data (dict): a data object returned by hf.initialize()
        name (str): name of either a group, singleton, or dataset the metadata corresponds to.
                    if passing a dataset name, make sure it is the full path (group/dataset)!
        meta_data (list): list of metadata to write to that group/dataset/singleton
    """

    if name in data["_META_"].keys():
        warnings.warn(
            f"This name {name} already has metadata in the hepfile data, skipping!"
        )
        return

    data["_META_"][name] = meta_data  # empty list for metadata


################################################################################
def pack(
    data: dict,
    bucket: dict,
    AUTO_SET_COUNTER: bool = True,
    EMPTY_OUT_BUCKET: bool = True,
    STRICT_CHECKING: bool = False,
    verbose: bool = False,
):
    """Takes the data from an bucket and packs it into the data dictionary,
    intelligently, so that it can be stored and extracted efficiently.
    (This is analagous to the ROOT TTree::Fill() member function).

    Args:
        data (dict): Data dictionary to hold the entire dataset EDIT.

        bucket (dict): bucket to be packed into data.

        EMPTY_OUT_BUCKET (bool): If this is `True` then empty out the `bucket`
                                container in preparation for the next iteration.
                                We used to ask the users to do this "by hand" but
                                now do it automatically by default. We allow the user to
                                not do this, if they are running some sort of debugging.

    """

    # Calculate the number of entries for each group and set the
    # value of that counter
    # This is all done in bucket
    if AUTO_SET_COUNTER:
        for group in data["_GROUPS_"]:
            if verbose:
                print(f"group: {group}")

            datasets = data["_GROUPS_"][group]
            counter = data["_MAP_DATASETS_TO_COUNTERS_"][group]
            if counter == "_SINGLETONS_GROUP_/COUNTER":
                continue

            # Here we will calculate the values for the counters, based
            # on the size of the datasets
            counter_value = None

            # Loop over the datasets
            for dset in datasets:
                full_dataset_name = group + "/" + dset
                # Skip any counters
                if counter == full_dataset_name:
                    continue

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
                if counter_value is None:
                    counter_value = temp_counter_value
                    bucket[counter] = temp_counter_value
                elif counter_value != temp_counter_value:
                    # In this case, we found two groups of different length!
                    # Print this to help the user identify their error
                    err = ""
                    for tempd in datasets:
                        temp_full_dataset_name = group + "/" + tempd
                        # Don't worry about the dataset
                        if counter == temp_full_dataset_name:
                            continue
                        err += f"{tempd}: {len(bucket[temp_full_dataset_name])}\n"

                    # Raise an exception for the external program to catch.
                    raise DatasetSizeDiscrepancy(
                        f"Oh no!!!! Two datasets in group {group} have different sizes! {err}"
                    )

    # Then pack the bucket into the data
    keys = list(bucket.keys())

    for key in keys:
        if key in {
            "_MAP_DATASETS_TO_COUNTERS_",
            "_GROUPS_",
            "_LIST_OF_COUNTERS_",
            "_MAP_DATASETS_TO_DATA_TYPES_",
            "_META_",
            "_PROTECTED_NAMES_",
        }:
            continue

        # The singletons will only have 1 entry per bucket
        if key == "_SINGLETONS_GROUP_/COUNTER":
            data[key].append(1)
            continue

        if isinstance(bucket[key], list):
            value = bucket[key]
            if len(value) > 0:
                data[key] += value
        else:
            # This is for counters and SINGLETONS
            if key in data["_GROUPS_"]["_SINGLETONS_GROUP_"]:
                if bucket[key] is None:
                    raise MissingSingletonValue(
                        f"\n\033[1m{key}\033[0m is part of the SINGLETON group \
                        and is expected to have a value for each bucket. However it is None!"
                    )

                # Append the single value from the singletons
                data[key].append(bucket[key])
            # Append the values to the counters
            else:
                data[key].append(bucket[key])

    # Clear out the bucket after it's been packed if that's what we want
    if EMPTY_OUT_BUCKET:
        clear_bucket(bucket)

    return 0


################################################################################


def _convert_list_and_key_to_string_data(datalist: list[any], key: str) -> str:
    """Converts data dictionary to a string

    Args:
        datalist (list): A list to be saved as a string.

    Returns:
        key (string): We will assume that this will be unpacked as a dictionary,
                      and this will be the key for the list in that dictionary.

    """
    stra = np.string_(key)

    mydataset = []
    strb = np.string_("")
    nvals = len(datalist)
    for i, val in enumerate(datalist):
        strb += np.string_(val)
        if i < nvals - 1:
            strb += np.string_("__:__")
    mydataset.append([stra, strb])

    return mydataset


################################################################################


################################################################################
def _convert_dict_to_string_data(dictionary: dict) -> str:
    """Converts data dictionary to a string

    Args:
        dictionary (dict): Dictionary to be converted to a string

    Returns:
        mydataset (string): String representation of the dataset

    """

    mydataset = []
    for key in dictionary:
        astr = np.string_(key)
        bstr = np.string_(dictionary[key])
        mydataset.append([astr, bstr])

    return mydataset


################################################################################
# This function writes default attributes and metadata to a file.
################################################################################
def write_file_metadata(
    filename: str,
    mydict: dict = None,
    write_default_values: bool = True,
    append: bool = True,
) -> h5.File:
    """Writes file metadata in the attributes of an HDF5 file

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

    with h5.File(filename, "a") as hdoutfile:
        # hdoutfile = h5.File(filename, "a")

        non_metadata = ["_NUMBER_OF_BUCKETS_"]

        if not append:
            for key in hdoutfile.attrs:
                if key not in non_metadata:
                    del hdoutfile.attrs[key]

        if write_default_values:
            hdoutfile.attrs["date"] = datetime.datetime.now().isoformat(sep=" ")
            hdoutfile.attrs["hepfile_version"] = hepfile.__version__
            hdoutfile.attrs["numpy_version"] = np.__version__
            hdoutfile.attrs["h5py_version"] = h5.__version__
            hdoutfile.attrs["awkward_version"] = ak.__version__
            hdoutfile.attrs["python_version"] = sys.version

        if mydict is not None:
            for key in mydict:
                hdoutfile.attrs[key] = mydict[key]

    print("Metadata added")
    return hdoutfile


################################################################################
# This function writes a set of user-defined header information to the
# hepfile
################################################################################
def write_file_header(filename: str, mydict: dict) -> h5.File:
    """Writes header data to a protected group in an HDF5 file.

        If there is already header information, it is overwritten
        by this function.

    Args:
    filename (string): Name of file to write to (file should already exist
                       and the group will be appended to it.)

    mydict (dictionary): Header data passed in by user

    Returns:
    hdoutfile (HDF5): Returns the file with new metadata

    """

    if len(mydict.keys()) == 0:
        raise InputError("Please provide header data to write to the header!")

    with h5.File(filename, "a") as hdoutfile:
        # We are going to write *all* the values as strings. The user can
        # change the type upon reading, if they so choose.
        dtype = h5.string_dtype(encoding="utf-8")

        # If the _HEADER_ group exists, delete it.
        header_group = None
        if "_HEADER_" in hdoutfile:
            del hdoutfile["_HEADER_"]

        header_group = hdoutfile.create_group("_HEADER_")

        for key in mydict.keys():
            values = mydict[key]

            # check that values can be converted to a np.array
            try:
                values = np.array(values)
            except Exception as err:
                raise InputError(
                    "Unable to convert header data to a numpy array!"
                ) from err

            # If value is just a str, int, or float, make it an array
            if isinstance(values, (str, float, int)):
                values = values.astype(str)

            # When we pass in the values, we need to do it as a list (NOT SURE WHY?)
            header_group.create_dataset(
                key, (len(values), 1), dtype=dtype, data=values.tolist()
            )

    # DO WE WANT TO DO THIS HERE?
    hdoutfile.close()

    print("Header data added")
    return hdoutfile


################################################################################

################################################################################


################################################################################
def write_to_file(
    filename: str,
    data: dict,
    comp_type: str = None,
    comp_opts: list = None,
    force_single_precision: bool = True,
    verbose: bool = False,
) -> h5.File:
    """Writes the selected data to an HDF5 file

    Args:
        filename (string): Name of output file

        data (dictionary): Data to be written into output file

        comp_type (string): Type of compression

        force_single_precision (boolean): True if data should be written in single precision

    Returns:
        hdoutfile (HDF5): File to which the data has been written

    """

    # hdoutfile = h5.File(filename, "w")

    with h5.File(filename, "w") as hdoutfile:
        groups = data["_GROUPS_"].keys()

        # Convert this to a 2xN array for writing to the hdf5 file.
        # This gives us one small list of informtion if we need to pull out
        # small chunks of data
        mydataset = _convert_dict_to_string_data(data["_MAP_DATASETS_TO_COUNTERS_"])
        hdoutfile.create_dataset(
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

        hdoutfile.create_dataset(
            "_SINGLETONSGROUPFORSTORAGE_",
            data=mydataset,
            dtype="S256",
            compression=comp_type,
            compression_opts=comp_opts,
        )

        for group in groups:
            hdoutfile.create_group(group)
            hdoutfile[group].attrs["counter"] = np.string_(
                data["_MAP_DATASETS_TO_COUNTERS_"][group]
            )

            if group in data["_META_"].keys():
                hdoutfile[group].attrs["meta"] = np.string_(data["_META_"][group])

            datasets = data["_GROUPS_"][group]

            for dataset in datasets:
                name = None
                if group == "_SINGLETONS_GROUP_" and dataset != "COUNTER":
                    name = dataset
                else:
                    name = f"{group}/{dataset}"

                if verbose is True:
                    print(f"Writing {name} to file")

                x = data[name]

                dataset_dtype = data["_MAP_DATASETS_TO_DATA_TYPES_"][name]

                if isinstance(x, list):
                    if verbose is True:
                        print("\tConverting list to array...")
                    x = np.array(x)

                # Do single precision only, unless specified
                if force_single_precision:
                    # different type calls depending on input datastructure
                    if isinstance(x, np.ndarray):
                        dtype = x.dtype
                    elif isinstance(x, (ak.Array, ak.Record)):
                        dtype = x.type
                    else:
                        dtype = None
                        warnings.warn(
                            "Not a proper data type to convert to single precision, skipping!"
                        )

                    if dtype == np.float64:
                        if verbose is True:
                            print("\tConverting array to single precision...")
                        x = x.astype(np.float32)
                        dataset_dtype = np.float32

                if dataset_dtype is not str:
                    if verbose is True:
                        print("\tWriting to file...")

                    hdoutfile.create_dataset(
                        name,
                        data=x,
                        compression=comp_type,
                        compression_opts=comp_opts,
                        dtype=dataset_dtype,
                    )
                else:
                    # For writing strings, we need to make sure our strings are ascii
                    # and not Unicode
                    #
                    # See my question on StackOverflow and the super-helpful response!
                    #
                    # https://stackoverflow.com/questions/68500454/can-i-use-h5py-to-write-strings-to-an-hdf5-file-in-one-line-rather-than-looping
                    dataset_dtype = h5.special_dtype(vlen=str)
                    longest_word = len(max(x, key=len))
                    arr = np.array(x, dtype="S" + str(longest_word))
                    hdoutfile.create_dataset(
                        name,
                        data=arr,
                        dtype=dataset_dtype,
                        compression=comp_type,
                        compression_opts=comp_opts,
                    )

                # write the dataset metadata if there is some
                if name in data["_META_"]:
                    hdoutfile[name].attrs["meta"] = np.string_(data["_META_"][name])

                if verbose:
                    print(f"Writing to file {name} as type {str(dataset_dtype)}")

        # Get the number of buckets
        counters = data["_LIST_OF_COUNTERS_"]
        num_buckets = -1
        prevcounter = None
        for i, countername in enumerate(counters):
            ncounter = len(data[countername])

            if verbose:
                print(f"{countername:<32s} has {ncounter:<12d} entries")

            if i > 0 and ncounter != num_buckets:
                warnings.warn(
                    f"{countername} and {prevcounter} have differing numbers of entries!"
                )
                # SHOULD WE EXIT ON THIS?

            num_buckets = max(num_buckets, ncounter)

            prevcounter = countername

        hdoutfile.attrs["_NUMBER_OF_BUCKETS_"] = num_buckets
        # hdoutfile.close()

    write_file_metadata(filename)

    return hdoutfile
