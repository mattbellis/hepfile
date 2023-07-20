"""
Tools to work with Pandas DataFrames and Hepfile data

Note: The base installation package does not contain these tools!
You must have installed hepfile with either \n
1) :code:`python -m pip install hepfile[pandas]`, or \n
2) :code:`python -m pip install hepfile[all]`
"""
from __future__ import annotations

import pandas as pd
import hepfile as hf
from hepfile.errors import InputError, MissingOptionalDependency
from hepfile.dict_tools import dictlike_to_hepfile


def hepfile_to_df(
    data: dict,
    groups: list[str] = None,
    events: list[int] = None,
) -> dict[pd.DataFrame]:
    """
    Converts hepfile data to dataframes where each group is in its own dataframe
    and we add an extra column called 'event_num'. Singletons have its own df

    Args:
        data (dict): data object either loaded from a hepfile or about to be
                     written to a hepfile.
        groups (list): groups to include, None (default) means include all groups
        events (list): list of event indexes to include

    Returns:
        dict[pd.DataFrame]: Dictionary of requested groups as dataframes where
                            the keys are the group names. If only one group is
                            requested then it just returns a dataframe of that
                            group.

    Raises:
        InputError: Something is wrong with the specified input
    """

    dfs = {}  # list to of dataframes to return

    # check inputs
    if groups is not None and not isinstance(groups, (list, str)):
        raise InputError("groups must be either a list or a string")

    if events is not None and not isinstance(events, (list, int)):
        raise InputError("events must be either a list or int")

    if isinstance(groups, str):
        groups = [groups]

    if isinstance(events, int):
        events = [events]

    if groups is None:
        groups = data["_GROUPS_"].keys()

    if not all(group in data["_GROUPS_"] for group in groups):
        raise InputError("Groups must be a subset of the group names in data!")

    # 1) regular groups to a dataframe for each group
    # 2) all singletons to a dataframe
    counters = set(data["_MAP_DATASETS_TO_COUNTERS_"].values())
    for group in groups:
        datasets = data["_GROUPS_"][group]

        # put the data for that group in a dictionary
        for_df = {}
        dataset = None
        for dataset in datasets:
            name = f"{group}/{dataset}"
            if name in counters:
                continue
            if group == "_SINGLETONS_GROUP_" and dataset in data:
                for_df[dataset] = data[dataset]
            else:
                if name in data:
                    for_df[dataset] = data[name]

        # compute the event numbers
        counter_name = data["_MAP_DATASETS_TO_COUNTERS_"][group]
        counters_for_df = []
        for i, counter in enumerate(data[counter_name]):
            for _ in range(counter):
                counters_for_df.append(i)
        for_df["event_num"] = counters_for_df

        group_df = pd.DataFrame(for_df)  # make for_df a df
        # get rid of anything not in events
        if events is None:
            events = group_df.event_num.unique()

        group_df = group_df[group_df.event_num.isin(events)]

        dfs[group] = group_df

    if len(dfs) == 1:
        return dfs[list(dfs.keys())[0]]
    return dfs


def awkward_to_df(
    ak_array: ak.Array,  # noqa: F821
    groups: list[str] = None,
    events: list[int] = None,
) -> dict[pd.DataFrame]:
    """
    Converts an awkward array of hepfile data to a dataframe. Does the same thing
    as hepfile_to_df but given an awkward array.

    Note: You must have installed with :code:`python -m pip install hepfile[all]`
          to use this tool!

    Args:
        ak_array (ak.Array): awkward array in the format of a hepfile
        groups (list): groups to include, None (default) means include all groups
        events (list): list of event indexes to include

    Returns:
        dict[pd.DataFrame]: Dictionary of requested groups as dataframes where the
                            keys are the group names. If only one group is
                            requested then it just returns a dataframe of that
                            group.

    Raises:
        MissingOptionalDependency: If you do not have the optional dependency awkward
                                   installed.
        InputError: If something is wrong with the specified input values.
    """

    if not hf._AWKWARD:
        raise MissingOptionalDependency("awkward")

    import awkward as ak

    dfs = {}  # list to of dataframes to return

    # check inputs
    if groups is not None and not isinstance(groups, (list, str)):
        raise InputError("groups must be either a list or a string")

    if events is not None and not isinstance(events, (list, int)):
        raise InputError("events must be either a list or int")

    if isinstance(groups, str):
        groups = [groups]

    if isinstance(events, int):
        events = [events]

    if groups is None:
        groups = ak_array.fields

    if not all(group in ak_array.fields for group in groups):
        raise InputError("Groups must be a subset of the group names in data!")

    for group in groups:
        # convert the record
        group_df = ak.to_dataframe(ak_array[group])

        # caluclate the indexes
        num = []
        for i, awk in enumerate(ak_array[group]):
            if isinstance(awk, (ak.Array, ak.Record)):
                record_len = len(awk.to_list()[awk.fields[0]])
                for _ in range(record_len):
                    num.append(i)
            else:
                num.append(i)

        # put event number in the dataframe
        group_df["event_num"] = num

        # only take events with event numbers in events
        if events is None:
            events = group_df.event_num.unique()
        group_df = group_df[group_df.event_num.isin(events)]

        dfs[group] = group_df

    if len(dfs) == 1:
        return dfs[list(dfs.keys())[0]]
    return dfs


def df_to_hepfile(
    df_dict: dict[pd.DataFrame],
    outfile: str = None,
    event_num_col="event_num",
    write_hepfile: bool = True,
) -> dict:
    """
    Converts a list of dataframes of group data to a hepfile. The opposite of
    hepfile_to_df. Must have an event_num column!

    Args:
        df_dict (dict): dictionary of pandas DataFrame groups to write to a hepfile
        outfile (str): output file name, required if write_hepfile is True
        event_num_col (str): name of a column in the pd.DataFrame to group by
        write_hepfile (bool): should we write the hepfile data to a hepfile?

    Returns:
        dict: hepfile data dictionary

    Raises:
        InputError: If something is wrong with the specific input.
    """

    out = groups_to_events(df_dict, event_num_col)
    return dictlike_to_hepfile(
        out,
        outfile=outfile,
        how_to_pack="classic",
        write_hepfile=write_hepfile,
        ignore_protected=True,
    )


def groups_to_events(
    df_dict: dict[pd.DataFrame], event_num_col: str = "event_num"
) -> dict:
    """
    Converts a dictionary of group dataframes to a dictionary of event dataframes

    Args:
        df_dict [dict] : dictionary of groups to convert to a dictionary of events
        event_num_col [str] : column to group each group by

    Returns:
        dict[pd.DataFrame]: dictionary of pandas dataframes organized by events

    Raises:
        InputError: Something is wrong with the input dictionary
    """

    out = {}
    all_subkeys = {}
    for group_name, data in df_dict.items():
        if group_name != "_SINGLETONS_GROUP_":
            all_subkeys[group_name] = set(data.columns)

        if event_num_col not in data.columns:
            raise InputError(
                f"{event_num_col} not in group {group_name} in the input dictionary"
            )

        groups = data.groupby(event_num_col)
        split_groups = [groups.get_group(item) for item in groups.groups]

        for grouping in split_groups:
            key = grouping[event_num_col].values[0]
            if key not in out:
                out[key] = {}

            if group_name != "_SINGLETONS_GROUP_" and group_name not in out[key]:
                out[key][group_name] = {}

            for colname in grouping.columns:
                if colname == event_num_col:
                    to_write = key
                    out[key][colname] = to_write
                elif group_name == "_SINGLETONS_GROUP_":
                    vals = grouping[colname].values
                    if len(vals) == 1:
                        to_write = vals[0]
                    else:
                        to_write = vals
                    out[key][colname] = to_write
                else:
                    to_write = list(grouping[colname].values)
                    out[key][group_name][colname] = to_write

    out = list(out.values())

    # check that the keys of each event are the same
    for event in out:
        missing1 = list(all_subkeys.keys() - event.keys())
        for key1 in missing1:
            if key1 != event_num_col:
                event[key1] = {}

        for group_name in event:
            if group_name == event_num_col or not isinstance(event[group_name], dict):
                continue
            missing = list(all_subkeys[group_name] - event[group_name].keys())
            for key in missing:
                if key != event_num_col:
                    event[group_name][key] = []
    return out
