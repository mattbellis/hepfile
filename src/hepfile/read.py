'''
Functions to assist in reading and accessing information in hepfiles.
'''

from __future__ import annotations

import warnings
import h5py as h5
import numpy as np
import pandas as pd
from . import constants
from .errors import RangeSubsetError, InputError, MetadataNotFound, HeaderNotFound
from .awkward_tools import hepfile_to_awkward

################################################################################
def load(
    filename: str,
    verbose: bool = False,
    desired_groups: list[str] = None,
    subset: int = None,
    return_awkward: bool = False,
) -> tuple[dict, dict]:
    """
    Reads all, or a subset of the data, from the HDF5 file to fill a data dictionary.
    Returns an empty dictionary to be filled later with data from individual buckets.

    Args:
        filename (string): Name of the input file

        verbose (boolean): True if debug output is required

        desired_groups (list): Groups to be read from input file,

        subset (int): Number of buckets to be read from input file

        return_awkward (boolean): If True, returns an awkward array Record. Default is False

    Returns:
        data (dict): Selected data from HDF5 file

        bucket (dict): An empty bucket dictionary to be filled by data from select buckets

    """

    with h5.File(filename, "r+") as infile:
        # Create the initial data and bucket dictionary to hold the data
        data = {}
        bucket = {}

        # We'll fill the data dictionary with some extra fields, though we won't
        # need them all for the bucket
        data["_MAP_DATASETS_TO_COUNTERS_"] = {}
        data["_MAP_DATASETS_TO_INDEX_"] = {}
        data["_LIST_OF_COUNTERS_"] = []
        data["_LIST_OF_DATASETS_"] = []
        data["_META_"] = {}

        # Get the number of buckets.
        # In HEP (High Energy Physics), this would be the number of events
        data["_NUMBER_OF_BUCKETS_"] = infile.attrs["_NUMBER_OF_BUCKETS_"]

        # We might only read in a subset of the data though!
        if subset is not None:
            if isinstance(subset, tuple):
                subset = list(subset)

            if isinstance(subset, int):
                print(
                    "Single subset value of {subset} being interpreted as a high range"
                )
                print(f"subset being set to a range of (0,{subset})\n")
                subset = [0, subset]

            # If the user has specified `subset` incorrectly, then let's return
            # an empty data and bucket
            if subset[1] - subset[0] <= 0:
                raise RangeSubsetError(
                    f"The range in subset is either 0 or negative! \
                    {subset[1]} - {subset[0]} = {subset[1] - subset[0]}"
                )

            # Make sure the user is not asking for something bigger than the file!
            nbuckets = data["_NUMBER_OF_BUCKETS_"]

            if subset[0] > nbuckets:
                raise RangeSubsetError(
                    f"Range for subset starts greater than number of buckets \
                    in file! {subset[0]} > {nbuckets}"
                )

            if subset[1] > nbuckets:
                warnings.warn(
                    f"Range for subset is greater than number of buckets in \
                    file!\n{subset[1]} > {nbuckets}\nHigh range of subset will \
                    be set to {nbuckets}\n"
                )
                subset[1] = nbuckets

            data["_NUMBER_OF_BUCKETS_"] = subset[1] - subset[0]
            nbuckets = data["_NUMBER_OF_BUCKETS_"]

            print("Will read in a subset of the file!")
            print(
                f"From bucket {subset[0]} (inclusive) through bucket {subset[1]-1} (inclusive)"
            )
            print(f"Bucket {subset[1]} is not read in")
            print(f"Reading in {nbuckets} buckets\n")

        ############################################################################
        # Get the datasets and counters
        ############################################################################
        allvalues = infile["_MAP_DATASETS_TO_COUNTERS_"]
        for vals in allvalues:
            if verbose:
                print(f"Map datasets to counters: {vals}")

            # The decode is there because vals were stored as numpy.bytes
            counter = vals[1].decode()
            index = f"{counter}_INDEX"
            data["_MAP_DATASETS_TO_COUNTERS_"][vals[0].decode()] = counter
            data["_MAP_DATASETS_TO_INDEX_"][vals[0].decode()] = index
            data["_LIST_OF_COUNTERS_"].append(vals[1].decode())
            data["_LIST_OF_DATASETS_"].append(vals[0].decode())
            data["_LIST_OF_DATASETS_"].append(
                vals[1].decode()
            )  # Get the counters as well

        # We may have added some counters and datasets multiple times.
        # So just to be sure, only keep the unique values
        data["_LIST_OF_COUNTERS_"] = np.unique(data["_LIST_OF_COUNTERS_"]).tolist()
        data["_LIST_OF_DATASETS_"] = np.unique(data["_LIST_OF_DATASETS_"]).tolist()
        ############################################################################

        ############################################################################
        # Pull out the SINGLETON datasets
        ############################################################################
        singletons_group = infile["_SINGLETONSGROUPFORSTORAGE_"][
            0
        ]  # This is a numpy array of strings
        decoded_string = singletons_group[1].decode()

        vals = decoded_string.split("__:__")
        vals.remove("COUNTER")

        data["_SINGLETONS_GROUP_"] = vals
        ############################################################################

        ############################################################################
        # Get the list of datasets and groups
        ############################################################################
        all_datasets = data["_LIST_OF_DATASETS_"]

        if verbose:
            print(f"all_datasets: {all_datasets}")
        ############################################################################

        ############################################################################
        # Only keep select data from file, if we have specified desired_groups
        ############################################################################
        if desired_groups is not None:
            if not isinstance(desired_groups, list):
                desired_groups = list(desired_groups)

            # Count backwards because we'll be removing stuff as we go.
            i = len(all_datasets) - 1
            while i >= 0:
                entry = all_datasets[i]

                is_dropped = True
                # This is looking to see if the string is anywhere in the name
                # of the dataset
                for desdat in desired_groups:
                    if desdat in entry:
                        is_dropped = False
                        break

                if is_dropped is True:
                    print(f"Not reading out {entry} from the file....")
                    all_datasets.remove(entry)

                i -= 1

            if verbose:
                print("After only selecting certain datasets ----- ")
                print(f"all_datasets: {all_datasets}")
        ###########################################################################

        # We might need the counter for SINGLETONS so let's pull it out
        data["_SINGLETONS_GROUP_/COUNTER"] = infile["_SINGLETONS_GROUP_"]["COUNTER"]

        if verbose:
            print("\nDatasets and counters:")
            print(data["_MAP_DATASETS_TO_COUNTERS_"])
            print("\nList of counters:")
            print(data["_LIST_OF_COUNTERS_"])
            print("\n_SINGLETONS_GROUP_/COUNTER:")
            print(data["_SINGLETONS_GROUP_/COUNTER"])
            print("\n")

        ############################################################################
        # Pull out the counters and build the indices
        ############################################################################
        print("Building the indices...\n")

        if verbose:
            print("data.keys()")
            print(data.keys())
            print("\n")

        # We will need to keep track of the indices in the entire file
        # This way, if the user specifies a subset of the data, we have the full
        # indices already calculated
        full_file_indices = {}

        for counter_name in data["_LIST_OF_COUNTERS_"]:
            if verbose:
                print(f"counter name: ------------ {counter_name}\n")

            full_file_counters = infile[counter_name]
            full_file_index = calculate_index_from_counters(full_file_counters)

            if verbose:
                print(f"full file counters: {full_file_counters}\n")
                print(f"full file index: {full_file_index}\n")

            # If we passed in subset, grab that slice of the data from the file
            if subset is not None and subset[1] <= subset[0]:
                raise RangeSubsetError(
                    f"Unable to read anything in! High range of {subset[1]} is \
                    less than or equal to low range of {subset[0]}"
                )

            if subset is not None:
                # We tack on +1 to the high range of subset when we pull out the counters
                # and index because we want to get all of the entries for the last entry.
                data[counter_name] = infile[counter_name][subset[0] : subset[1] + 1]
                index = full_file_index[subset[0] : subset[1] + 1]
            else:
                data[counter_name] = infile[counter_name][:]
                index = full_file_index

            subset_index = index
            # If the file is *not* empty....
            # Just to make sure the "local" index of the data dictionary starts at 0
            if len(index) > 0:
                subset_index = index - index[0]

            index_name = f"{counter_name}_INDEX"

            data[index_name] = subset_index
            full_file_indices[index_name] = index

        print("Built the indices!")

        if verbose:
            print("full_file_index: ")
            print(f"{full_file_indices}\n")

        # Loop over the all_datasets we want and pull out the data.
        for name in all_datasets:
            # If this is a counter, we're going to have to grab the indices
            # differently than for a "normal" dataset
            is_counter = True
            index_name = None
            if name not in data["_LIST_OF_COUNTERS_"]:
                index_name = data["_MAP_DATASETS_TO_INDEX_"][name]
                is_counter = False  # We will use different indices for the counters

            if verbose:
                print(f"------ {name}")
                print(f"index_name: {index_name}\n")

            dataset = infile[name]

            if verbose:
                print(f"dataset type: {type(dataset)}")

            # This will ignore the groups
            if isinstance(dataset, h5.Dataset):
                dataset_name = name

                if subset is not None:
                    if is_counter:
                        # If this is a counter, then the subset indices
                        # map on to the same locations for any counters
                        lo = subset[0]
                        hi = subset[1]
                    else:
                        lo = full_file_indices[index_name][0]
                        hi = full_file_indices[index_name][-1]
                    if verbose:
                        print(f"dataset name/lo/hi: {dataset_name},{lo},{hi}\n")
                    data[dataset_name] = dataset[lo:hi]
                else:
                    data[dataset_name] = dataset[:]

                bucket[dataset_name] = None  # This will be filled for individual bucket
                if verbose:
                    print(dataset)

            # write the metadata for that group to data if it exists
            if name not in constants.protected_names and "meta" in dataset.attrs.keys():
                data["_META_"][name] = dataset.attrs["meta"]

    print("Data is read in and input file is closed.")

    # edit data so it matches the format of the data dict that was saved to the file
    # this makes it so that data can be directly passed to write_to_file
    # 1) add back in _GROUP_
    datasets = np.array(data["_LIST_OF_DATASETS_"])

    allgroups = np.array([d.split("/")[0] for d in datasets])

    singletons_group = set(data["_SINGLETONS_GROUP_"])
    groups = {}

    groups["_SINGLETONS_GROUP_"] = data["_SINGLETONS_GROUP_"]  # copy over the data

    for key in np.unique(allgroups):
        if key in singletons_group:
            continue
        if key in constants.protected_names:
            continue

        where_groups = np.where((key == allgroups) * (key != datasets))[0]
        groups[key] = [dataset.split("/")[-1] for dataset in datasets[where_groups]]

    data["_GROUPS_"] = groups

    # 2) add back in _MAP_DATASETS_TO_DATA_TYPES
    dtypes = {}
    for key in data["_LIST_OF_DATASETS_"]:
        if key not in data:
            continue

        if isinstance(data[key], list):
            data[key] = np.array(data[key])

        dtypes[key] = data[key].dtype

    data["_MAP_DATASETS_TO_DATA_TYPES_"] = dtypes

    # 3) add _PROTECTED_NAMES_
    data["_PROTECTED_NAMES_"] = constants.protected_names

    if return_awkward:
        return hepfile_to_awkward(data), bucket

    return data, bucket


################################################################################


################################################################################
def calculate_index_from_counters(counters: int) -> int:
    '''
    Calculates an index array from the counters
    '''
    index = np.add.accumulate(counters) - counters

    return index


################################################################################


################################################################################
def unpack(bucket: dict, data: dict, n: int = 0):
    """Fills the bucket dictionary with selected rows from the data dictionary.

    Args:

        bucket (dict): bucket dictionary to be filled

        data (dict): Data dictionary used to fill the bucket dictionary

        n (integer): 0 by default. Which entry should be pulled out of the data
                     dictionary and inserted into the bucket dictionary.

    """

    keys = bucket.keys()

    for key in keys:
        # if "num" in key:
        # IS THERE A WAY THAT THIS COULD BE FASTER?
        # print(data['_LIST_OF_COUNTERS_'],key)
        if key in data["_LIST_OF_COUNTERS_"] or key in data["_SINGLETONS_GROUP_"]:
            bucket[key] = data[key][n]

        elif "INDEX" not in key:  # and 'Jets' in key:
            indexkey = data["_MAP_DATASETS_TO_INDEX_"][key]
            numkey = data["_MAP_DATASETS_TO_COUNTERS_"][key]

            if len(data[indexkey]) > 0:
                index = data[indexkey][n]

            if len(data[numkey]) > 0:
                nobjs = data[numkey][n]
                bucket[key] = data[key][index : index + nobjs]


################################################################################
def get_nbuckets_in_file(filename: str) -> int:
    """Get the number of buckets in the file."""

    # f = h5.File(filename, "r+")
    # a = f.attrs

    if not isinstance(filename, str):
        raise InputError("Expecting the input filename to be a string!")

    with h5.File(filename, "r+") as infile:
        attr = infile.attrs
        if "_NUMBER_OF_BUCKETS_" not in attr:
            raise AttributeError(
                'File does not contain the attribute, "_NUMBER_OF_BUCKETS_"'
            )

        num_buckets = attr.get("_NUMBER_OF_BUCKETS_")
        return num_buckets
    
################################################################################
def get_nbuckets_in_data(data: dict) -> int:
    """Get the number of buckets in the data dictionary.

    This is useful in case you've only pulled out subsets of the data

    """

    if not isinstance(data, dict):
        raise InputError(f"{data} is not a dictionary!\n")

    if "_NUMBER_OF_BUCKETS_" not in list(data.keys()):
        raise AttributeError(
            '\ndata dictionary does not contain the key, "_NUMBER_OF_BUCKETS_"\n'
        )
    num_buckets = data["_NUMBER_OF_BUCKETS_"]
    return num_buckets

################################################################################
def get_file_metadata(filename: str) -> dict:
    """Get the file metadata and return it as a dictionary"""

    with h5.File(filename, "r+") as infile:
        attrs = infile.attrs

        if len(attrs) < 1:
            raise MetadataNotFound(
                f"No metadata in file {filename}! File has no attributes.\n"
            )

        metadata = {}
        for key in attrs:
            metadata[key] = attrs[key]

    return metadata


################################################################################


################################################################################
def get_file_header(filename: str, return_type: str = "dict") -> dict:
    """Get the file header and return it as a dictionary or dataframe

    Args:
    filename(string): HDF5 file to open and read the header information

    return_type(string): If 'dict' return the header information as a dictionary.
                         If 'df' or 'dataframe', return the information as a
                         pandas dataframe.

    """

    if return_type is not None and return_type not in ["dict", "df", "dataframe"]:
        print("'return_type' must be 'dict', 'df', or 'dataframe'")
        print("Not returning any header information")
        return None

    with h5.File(filename, "r+") as infile:
        if "_HEADER_" not in infile:
            raise HeaderNotFound(
                f"No header data in file {filename}! File has no _HEADER_ group.\n"
            )
            
        header_group = infile["_HEADER_"]

        header = {}
        for key in header_group:
            # Let's decode the binary strings to make it easier on the user.
            values = header_group[key][:]
            temp = []
            for val in values:
                temp.append(val[0].decode())

            # Convert it to numpy array as that may be more expected for the user.
            header[key] = np.array(temp)

        if return_type in ("dataframe", "df"):
            header = pd.DataFrame.from_dict(header)

    return header


################################################################################
################################################################################
def print_file_metadata(filename: str):
    """Pretty print the file metadata"""

    output = ""

    try:
        metadata = get_file_metadata(filename)
    except MetadataNotFound:
        print(f"No Metadata in {filename}!")
        return output

    keys = list(metadata.keys())

    first_keys_to_print = ["date", "_NUMBER_OF_BUCKETS_"]

    keys_already_printed = []

    # Print the basics first
    for key in first_keys_to_print:
        if key in keys:
            val = metadata[key]
            output += f"{key:<20s} : {val}\n"
            keys_already_printed.append(key)

    # Print the versions next
    for key in keys:
        if key in keys_already_printed:
            continue

        if key.find("version") >= 0:
            val = metadata[key]
            output += f"{key:<20s} : {val}\n"
            keys_already_printed.append(key)

    # Print the read of the metadata
    for key in keys:
        if key in keys_already_printed:
            continue

        val = metadata[key]
        output += f"{key:<20s} : {val}\n"
        keys_already_printed.append(key)

    print(output)

    return output


################################################################################


def print_file_header(filename: str) -> str:
    """
    Pretty print the file header

    Args:
        filename (str): filename to retrieve the header from.

    Returns:
        String representation of the header information, if it exists.
    """

    hdr = get_file_header(filename, return_type="dict")

    return_str = f"{'#':#>64}\n"
    return_str += f"###{' ':>22}Hepfile Header{' ':>22}###\n"
    return_str += f"{'#':#>64}\n"
    return_str += f"{'#':#>64}\n"

    for key in hdr.keys():
        return_str += f"{key}:"
        for val in hdr[key]:
            return_str += f"\t\t\t{val}\n"

    print(return_str)
    return return_str
