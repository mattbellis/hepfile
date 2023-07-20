"""
These are tools to make working with and translating between awkward arrays
and hepfile data objects easier.

Note: The base installation package does not contain these tools!
You must have installed hepfile with either \n
1) :code:`python -m pip install hepfile[awkward]`, or \n
2) :code:`python -m pip install hepfile[all]`
"""
from __future__ import annotations

import warnings
import awkward as ak
import numpy as np
from hepfile.write import (
    initialize,
    write_to_file,
)
from hepfile.errors import AwkwardStructureError, InputError
from hepfile.constants import char_codes


################################################################################
def hepfile_to_awkward(
    data: dict, groups: list = None, datasets: list = None
) -> ak.Record:
    """
    Converts all (or a subset of) the output data from `hepfile.read.load` to
    a dictionary of awkward arrays.

    Args:
        data (dict): Output data dictionary from the `hepfile.read.load` function.
        groups (list): list of groups to pull from data and convert to awkward arrays.
        datasets (list): list of full dataset paths (ex. 'jet/px' not 'px') to pull
                         from data and include in the awkward arrays.

    Returns:
        dict: dictionary of awkward arrays with the data.

    Raises:
        AwkwardStructureError: If something is wrong with the awkward array being
                               outputted
        Warning: If it is returning an awkward Record rather than and awkward Array
    """

    if isinstance(groups, str):
        groups = [groups]

    if groups is None:
        groups = list(data["_GROUPS_"].keys())

    ak_arrays = {}

    # turn a few things into sets for faster searching
    list_of_counters = set(data["_LIST_OF_COUNTERS_"])
    singletons_group = set(data["_GROUPS_"]["_SINGLETONS_GROUP_"])

    for group in groups:
        for dset in data["_GROUPS_"][group]:
            if dset in singletons_group:
                dataset = dset
            else:
                dataset = f"{group}/{dset}"

            if dataset in list_of_counters:
                continue

            if dataset not in data.keys():
                continue

            if datasets is not None and dataset not in datasets:
                continue

            if (
                len(data[dataset]) != 0
                and isinstance(data[dataset], (np.ndarray, list))
                and isinstance(data[dataset][0], bytes)
            ):
                data[dataset] = np.array([val.decode() for val in data[dataset]])

            if dataset in singletons_group:
                if dataset in data.keys():  # skip if it isn't in data
                    ak_arrays[dataset] = ak.Array(data[dataset])
                continue

            nkey = data["_MAP_DATASETS_TO_COUNTERS_"][dataset]

            num = data[nkey]
            vals = data[dataset]

            # ak_array = ak.unflatten(list(vals), list(num))
            ak_array = ak.unflatten(vals, num)

            if group not in ak_arrays:
                ak_arrays[group] = {}
            ak_arrays[group][dset] = ak_array

    try:
        awk = ak.Array(ak_arrays)
    except ValueError:
        warnings.warn(
            "Cannot convert to an Awkward Array because dict arrays have"
            + " different lengths! Returning an Awkward Record instead."
        )
        awk = ak.Record(ak_arrays)

    try:
        _is_valid_awkward(awk)
    except AwkwardStructureError as err:
        print(err)
        raise AwkwardStructureError(
            "Cannot convert to proper awkward array because of the above \
            error! Check your input hepfile format"
        ) from err

    return awk


################################################################################
def pack_single_awkward_array(
    data: dict,
    arr: ak.Array,
    dset_name: str,
    group_name: str = None,
    counter: str = None,
) -> None:
    """
    Packs a 1D awkward array as a dataset/singleton depending on if group_name is given

    Args:
        data (dict): data dictionary created by hepfile.initialize()
        arr (ak.Array): 1D awkward array to pack as either a dataset or a group.
                        If group_name is None the arr is packed as a singleton
        dset_name (str): Full path to the dataset.
        group_name (str): name of the group to pack the arr under, default is None
        counter (str): name of the counter in the hepfile for this dataset

    Raises:
        InputError: If it can not extract the datatype of the values in `arr`
    """
    if group_name is not None:
        if counter is None:
            counter = f"{group_name}/n{group_name}"

        # add the counter to the groups dictionary if it is not already in it
        if group_name not in data["_GROUPS_"]:
            data["_GROUPS_"][group_name] = [counter.split("/")[1]]

            # We will use this name for the counter later
            data["_MAP_DATASETS_TO_DATA_TYPES_"][counter] = int

            data["_MAP_DATASETS_TO_COUNTERS_"][group_name] = counter
            data["_LIST_OF_COUNTERS_"].append(counter)

    else:
        counter = "_SINGLETONS_GROUP_/COUNTER"

    # Tells us if this is jagged or not
    if arr.ndim == 1:
        # Get the datatpe before we flatten it
        if len(arr) == 0:
            dtype = None
        else:
            dtype = _get_awkward_type(arr)

        num = np.ones(len(arr), dtype=int)
        np_arr = ak.to_numpy(arr)

    else:
        # Get the datatpe before we flatten it
        if len(arr[0]) == 0:
            dtype = None
        else:
            dtype = _get_awkward_type(arr)

        # This saves the counter as int64, taking up a bit more space
        # Probably minimal though.
        # num = ak.num(x)
        # This saves the counter as int32
        num = ak.to_numpy(ak.num(arr)).astype(np.int32)
        np_arr = ak.flatten(arr).to_numpy()

    data[dset_name] = np_arr

    # Not a SINGLETON, the user has passed in a groupname
    if group_name is not None:
        data["_MAP_DATASETS_TO_DATA_TYPES_"][dset_name] = dtype
        data["_MAP_DATASETS_TO_COUNTERS_"][dset_name] = counter
        data["_GROUPS_"][group_name].append(dset_name.split("/")[1])
        if counter not in data:
            data[counter] = num

    # If it is a SINGLETON
    else:
        data["_MAP_DATASETS_TO_DATA_TYPES_"][dset_name] = dtype
        data["_MAP_DATASETS_TO_COUNTERS_"][dset_name] = "_SINGLETONS_GROUP_/COUNTER"
        data["_GROUPS_"]["_SINGLETONS_GROUP_"].append(dset_name)
        if len(data[counter]) == 0:
            data[counter] = num


def pack_multiple_awkward_arrays(
    data: dict, arr: ak.Array, group_name: str = None, group_counter_name: str = None
) -> None:
    """
    Pack an awkward array of arrays into group_name or the singletons group

    Args:
        data (dict): hepfile data dictionary that is returned from hepfile.initialize()
        arr (ak.Array): Awkward array of the group in a set of data
        group_name (str): Name of the group to pack arr into, if None (default) it is
                          packed into the signletons group

    Raises:
        InputError: If input awkward array doesn't have any fields, if this happens
                     consider using pack_single_awkward_array. Also happens if the input
                     is not an awkward array and can not be converted.
    """

    # If the user passed in a group, then the datasets will
    # be under that group

    # check that arr is an awkward array
    if not isinstance(arr, (ak.Array, ak.Record)):
        try:
            arr = ak.Array(arr)
        except Exception as exc:
            raise InputError("Cannot convert your input to an awkward array!") from exc

    if len(arr.fields) == 0:
        raise InputError(
            "The input awkward array must have at least one field value! "
            + "If this is a singleton just provide the name of the singleton "
            + "as the field"
        )
    # Loop over the dictionary that is passed in
    for field in arr.fields:
        # build a name for the hepfile entry
        if group_name is None:
            # these are singletons
            dataset_name = field
        else:
            # these are regular groups with datasets
            dataset_name = f"{group_name}/{field}"

        pack_single_awkward_array(
            data,
            arr[field],
            dataset_name,
            group_name=group_name,
            counter=group_counter_name,
        )


def awkward_to_hepfile(
    ak_array: ak.Array, outfile: str = None, write_hepfile: bool = True, **kwargs
) -> dict:
    """
    Write an awkward array with depth <= 2 to a hepfile

    Args:
        ak_array (ak.Array): awkward array with fields of groups/singletons.
                             Under the group fields are the dataset fields.
        outfile (str): path to where the hepfile should be written. Default is None
                       and can only be None if write_hepfile=False.
        write_hepfile (bool): if True, write the hepfile and return the data dictionary.
                              If False, just return the data dictionary without
                              returning. Default is True.
        **kwargs: passed to `hepfile.write_to_file`

    Returns:
        dict: Data dictionary in the hepfile

    Raises:
        AwkwardStructureError: If the input awkward array is not formatted properly.
        InputError: If something is wrong with the specified input
        Warning: If write_hepfile is false but you still give an output path
    """

    _is_valid_awkward(ak_array)

    if write_hepfile is True and outfile is None:
        raise InputError("Please provide an outfile path if write_hepfile=True!")

    if write_hepfile is False and outfile is not None:
        warnings.warn(
            "You set write_hepfile to False but provided an output file path. \
            This output file path will not be used!"
        )

    data = initialize()
    for group in ak_array.fields:
        if len(ak_array[group].fields) == 0:
            # this is a singleton
            pack_multiple_awkward_arrays(data, {group: ak_array[group]})
        else:
            # these are datasets under group
            pack_multiple_awkward_arrays(data, ak_array[group], group_name=group)

    if write_hepfile:
        write_to_file(outfile, data)

    return data


def _awkward_depth_check(ak_array: ak.Record) -> int:
    for field in ak_array.fields:
        if not isinstance(ak_array[field], (ak.Record, ak.Array)):
            continue
        for subfield in ak_array[field].fields:
            if len(ak_array[field][subfield].fields) != 0:
                raise AwkwardStructureError(
                    "Hepfile only supports awkward arrays \
                with a depth <= 2! Please ensure your input follows this guideline"
                )


def _is_valid_awkward(ak_array: ak.Record):
    """
    Checks if the input awkward array is valid and raises an exception if not

    Args:
        ak_array (ak.Array): awkward array to check
    """

    # validate input array
    if not isinstance(ak_array, (ak.Array, ak.Record)):
        raise AwkwardStructureError("Please input an Awkward Array or Awkward Record")

    if len(ak_array.fields) == 0:
        raise AwkwardStructureError(
            "Your input Awkward Array must be a Record. \
            This means it needs to have fields in it."
        )

    # check input array only has a "depth" of 2
    # this can be removed once hepfiles support unlimited depth of groups!
    _awkward_depth_check(ak_array)


def _get_awkward_type(ak_array: ak.Record) -> type:
    """
    Private method to switch from awkward types to numpy types
    This is necessary because h5py does not understand awkward types
    """

    if isinstance(ak_array[0], (ak.Record, ak.Array)):
        arr = ak_array
        type_str = ak_array.type.content

        if isinstance(type_str, ak.types.NumpyType):
            dtype = type_str.primitive
        else:
            dtype = str(type_str).rsplit("*", maxsplit=1)[-1].strip()
    else:
        arr = np.array(ak_array)
        dtype = arr.dtype

    if dtype == "string":
        dtype = np.dtype("<U1")

    try:
        np_dtype = np.dtype(dtype)
        if np_dtype.kind not in char_codes:
            np_dtype = str

    except Exception as exc:
        raise InputError(
            "Cannot convert awkward data type to a numpy data type!"
        ) from exc

    return np_dtype
