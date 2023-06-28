"""
Functions to help convert dictionaries into hepfiles
"""
from __future__ import annotations

import awkward as ak
from .awkward_tools import awkward_to_hepfile, _is_valid_awkward
from .errors import AwkwardStructureError, DictStructureError, InputError
from .write import (
    initialize,
    write_to_file,
    create_dataset,
    create_group,
    pack,
    create_single_bucket,
)


def dictlike_to_hepfile(
    dict_list: list[dict], outfile: str = None, how_to_pack="awkward", **kwargs
) -> ak.Record:
    """
    This wraps on `hepfile.awkward_tools.awkward_to_hepfile`
    and writes a list of dictionaries to a hepfile.

    Writes a list of dictlike object to a hepfile. Must have a specific format:
    - each dictlike object is a "event"
    - first level of dict keys are the groups
    - second level of dict keys are the datasets
    - entries in second level of dict object is the data and can be either awkward arrays or lists
    - data entries in the first level of the dict are singleton objects

    Args:
        dict_list (list): list of dictionaries or dataframes where each dictionary/df
                          holds information on an event
        outfile (str): path to write output hepfile to
        how_to_pack (str): how to pack the input dataset. Options are 'awkward' or 'classic'.
                      'awkward' called awkward_to_hepfile, 'classic' does it more traditional.
                      default is 'awkward'.
        **kwargs: passed to `hepfile.write.write_to_file`
    Returns:
        Dictionary of Awkward Arrays with the data stored in outfile
    """

    # check if it is a list of dictionaries or dataframe
    if not isinstance(dict_list, list):
        try:  # try convert from dataframe to list of dictionaries
            dict_list = [dict_list[key].to_dict() for key in dict_list.to_dict()]
        except Exception as exc:
            raise InputError(
                "Please input either a dataframe or list \
            of dictionaries"
            ) from exc

    # validate input dictionary
    keys = dict_list[0].keys()
    for item in dict_list:
        if item.keys() != keys:
            raise InputError(
                "Keys must match across the entire input dictionary list!!!"
            )

    if how_to_pack == "awkward":
        return _awkward(dict_list, outfile, **kwargs)

    if how_to_pack == "classic":
        return _classic(dict_list, outfile)

    raise InputError("how_to_pack should either be 'awkward' or 'classic'")


def _classic(dict_list: dict, outfile: str) -> ak.Record:
    """Private method to convert a list of events to a hepfile using the traditional method"""

    if outfile is None:
        raise InputError(
            "outfile name can not be None for the classic writing algorithm"
        )

    # first create the group names and dataset names
    data = initialize()
    for group_name in dict_list[0]:
        temp_dict = dict_list[0]

        if not isinstance(temp_dict[group_name], dict):
            # this is a singleton

            test_list = temp_dict[group_name]
            if not isinstance(temp_dict[group_name], list):
                test_list = [temp_dict[group_name]]

            if len(test_list) == 0:
                dtype = None
            else:
                dtype = type(test_list[0])
            create_dataset(data, group_name, dtype=dtype)

            continue

        create_group(data, group_name, counter=f"n{group_name}")
        for dataset_name in temp_dict[group_name]:
            if not isinstance(temp_dict[group_name][dataset_name], list):
                raise DictStructureError("Subdictionaries must be made up of lists!")

            if len(temp_dict[group_name]) == 0:
                dtype = None
            else:
                dtype = type(temp_dict[group_name][dataset_name][0])
            create_dataset(data, dataset_name, group=group_name, dtype=dtype)

    # now pack the data from each data dictionary
    for data_dict in dict_list:
        bucket = create_single_bucket(data)
        for group in data_dict:
            group_name = group.replace("/", "-")
            if group in bucket["_GROUPS_"]["_SINGLETONS_GROUP_"]:
                bucket[group_name] = data_dict[group]
                continue

            for dataset in data_dict[group]:
                dataset_name = dataset.replace("/", "-")
                name = f"{group}/{dataset_name}"
                bucket[name] = data_dict[group][dataset]
        pack(data, bucket)

    # finally write the data out to a file
    write_to_file(outfile, data)
    return data


def _awkward(dict_list: list[dict], outfile: str = None, **kwargs):
    """Private method to convert a list of events to a hepfile using awkward arrays"""
    # convert dictionary list to  an awkward array and write to hepfile
    out_ak = ak.Array(dict_list)

    # catch an awkward structure error and instead return a dictionary structure error
    try:
        awkward_to_hepfile(out_ak, outfile, **kwargs)
    except AwkwardStructureError as err:
        raise DictStructureError(err) from err

    return out_ak


def append(ak_dict: ak.Record, new_dict: dict) -> ak.Record:
    """
    Append a new event to an existing awkward dictionary with events

    Args:
        ak_dict (ak.Record): awkward Record of data
        new_dict (dict): Dictionary of value to append to ak_dict. All keys must match ak_dict!
    Return:
        Awkward Record of awkward arrays with the new_dict appended
    """

    _is_valid_awkward(ak_dict)

    if sorted(list(new_dict.keys())) != sorted(ak_dict.fields):
        raise InputError(
            f"Keys of new array do not match keys of existing array!\nExisting \
            Array Keys: {ak_dict.fields}\nNew Dictionary Keys: {new_dict.keys()}"
        )

    ak_list = ak.to_list(ak_dict)
    ak_list.append(new_dict)
    return ak.Array(ak_list)
