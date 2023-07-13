"""
These are tools to make working with and translating between awkward arrays
and hepfile data objects easier.

Note: The base installation package does not contain these tools!
You must have installed hepfile with either
1) 'python -m pip install hepfile[awkward]', or
2) 'python -m pip install hepfile[all]'
"""
from __future__ import annotations

import warnings
import awkward as ak
import numpy as np
from hepfile.write import (
    initialize,
    create_group,
    create_dataset,
    write_to_file,
    create_single_bucket,
    pack,
)
from hepfile.errors import AwkwardStructureError, InputError


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
        ak_arrays (dict): dictionary of awkward arrays with the data.
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

            ak_array = ak.unflatten(list(vals), list(num))

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
def awkward_to_hepfile(
    ak_array: ak.Record,
    outfile: str = None,
    write_hepfile: bool = True,
    verbose: bool = False,
    **kwargs,
) -> dict:
    """
    Converts a dictionary of awkward arrays to a hepfile

    Args:
        ak_array (Awkward Array): dictionary of Awkward Arrays to write to a hepfile
        outfile (str): path to write output hdf5 file to
        write_hepfile (bool): if True, writes data to outfile.
                              If False, just converts to hepfile format and returns
        verbose (bool): if true print some stuff
        **kwargs (None): Passed to `hepfile.write.write_to_file`

    Returns:
        Dictionary of hepfile data
    """

    # perform IO checks

    _is_valid_awkward(ak_array)

    if write_hepfile is True and outfile is None:
        raise InputError("Please provide an outfile path if write_hepfile=True!")

    if write_hepfile is False and outfile is not None:
        warnings.warn(
            "You set write_hepfile to False but provided an output file path. \
            This output file path will not be used!"
        )

    data = initialize()
    # first create the named groups and datasets
    for group in ak_array.fields:
        counter = f"n{group}"

        # check for singletons
        if len(ak_array[group].fields) == 0:
            dtype = _get_awkward_type(ak_array[group])
            create_dataset(data, group, dtype=dtype)
            continue

        create_group(data, group, counter=counter)
        for dataset in ak_array[group].fields:
            if len(ak_array[group][dataset][0]) == 0:
                dtype = None
            else:
                dtype = _get_awkward_type(ak_array[group][dataset])
            create_dataset(data, dataset, group=group, dtype=dtype)

    # then pack data from the awkward array
    for data_dict in ak_array:
        bucket = create_single_bucket(data)
        for group in data_dict.fields:
            if group in bucket["_GROUPS_"]["_SINGLETONS_GROUP_"]:
                bucket[group] = data_dict[group]
                continue

            for dataset in data_dict[group].fields:
                name = f"{group}/{dataset}"
                bucket[name] = data_dict[group][dataset].to_list()
        pack(data, bucket)

    # then write it out to a file
    if write_hepfile:
        if verbose:
            print("Writing the hdf5 file from the awkward array...")

        write_to_file(outfile, data)

    return data


def _awkward_depth(ak_array: ak.Record) -> int:
    max_depth = 0
    for item in ak_array.to_list():
        item_depth = 0
        for string in str(item):
            if string == "{":
                item_depth += 1

            if item_depth > max_depth:
                max_depth = item_depth

            if string == "}":
                item_depth -= 1

    return max_depth


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
    if _awkward_depth(ak_array) > 2:
        raise AwkwardStructureError(
            "Hepfile only supports awkward arrays with a depth <= 2! \
            Please ensure your input follows this guideline."
        )


def _get_awkward_type(ak_array: ak.Record) -> type:
    ndim = ak_array.ndim
    try:
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

        np_dtype = np.dtype(dtype)
        if np_dtype.char == "U":
            np_dtype = str

    except Exception as exc:
        raise InputError("Cannot convert input value to a numpy data type!") from exc

    return np_dtype
