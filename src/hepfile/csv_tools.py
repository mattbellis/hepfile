"""
Tools to help with managing csvs with hepfile
"""
from __future__ import annotations

import os
from typing import Optional

import pandas as pd
import awkward as ak
from .dict_tools import dictlike_to_hepfile


def csv_to_lists(
    csvpaths: list[str], common_key: str, group_names: Optional[list] = None
) -> ak.Record:
    """
    Convert a list of csvs to an awkward array.
    This is really just used in a step to convert csvs to a hepfile

    Args:
        csvpaths (list[str]): list of absolute paths to the csvs to convert to a hepfile
        common_key (str): The above list of csvs should have a common column name,
                          give the name of this column
        group_names (list): the names for the groups in the hepfile. Default is
                            None and the groups are based on the filenames

    Returns:
        Awkward array record of the csvs
    """

    if group_names is None:
        group_names = [os.path.split(file)[-1] for file in csvpaths]

    # organize into events
    out = {}
    all_subkeys = {}
    for infile, group_name in zip(csvpaths, group_names):
        csv = pd.read_csv(infile)

        all_subkeys[group_name] = set(csv.columns)

        groups = csv.groupby(common_key)
        split_groups = [groups.get_group(item) for item in groups.groups]

        for grouping in split_groups:
            key = grouping[common_key].values[0]
            if key not in out:
                out[key] = {}

            if group_name not in out[key]:
                out[key][group_name] = {}

            for colname in grouping.columns:
                if colname == common_key:
                    to_write = key
                    out[key][colname] = to_write
                else:
                    to_write = list(grouping[colname].values)
                    out[key][group_name][colname] = to_write

    out = list(out.values())

    # check that the keys of each event are the same
    for event in out:
        missing1 = list(all_subkeys.keys() - event.keys())
        for key1 in missing1:
            if key1 != common_key:
                event[key1] = {}

        for group_name in event:
            if group_name == common_key:
                continue
            missing = list(all_subkeys[group_name] - event[group_name].keys())
            for key in missing:
                if key != common_key:
                    event[group_name][key] = []

    return out


def csv_to_hepfile(
    csvpaths: list[str],
    common_key: str,
    outfile: Optional[str] = None,
    group_names: Optional[list] = None,
    write_hepfile: bool = True,
) -> tuple[str, dict]:
    """
    Convert a list of csvs to a hepfile

    This is helpful for converting database-like csvs to a hepfile where
    each input csv has a common key and can be combined into a large table.

    Args:
        csvpaths (list[str]): list of absolute paths to the csvs to convert to a hepfile
        common_key (str): The above list of csvs should have a common column
                          name, give the name of this column
        outfile (str): The output file name, if None data is written to the
                       first filepath in csvpaths with 'csv' replaced with 'h5'
        group_names (list): the names for the groups in the hepfile. Default is
                            None and the groups are based on the filenames
        write_hepfile: (bool): if True, write the hepfile. Default is True.

    Returns:
        Dictionary of hepfile data
    """

    if outfile is None:
        outpath = csvpaths[0]
        outfile = outpath.replace(".csv", ".h5")

    event_dict = csv_to_lists(csvpaths, common_key, group_names=group_names)

    return outfile, dictlike_to_hepfile(
        event_dict, outfile=outfile, how_to_pack="classic", write_hepfile=write_hepfile
    )
