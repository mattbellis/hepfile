"""
Tools to help with managing csvs with hepfile

Note: The base installation package does not contain these tools!
You must have installed hepfile with either \n
1) :code:`python -m pip install hepfile[pandas]`, or \n
2) :code:`python -m pip install hepfile[all]`
"""
from __future__ import annotations

import os
from typing import Optional

import pandas as pd
from hepfile.df_tools import df_to_hepfile


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
        Tuple(str, dict): path to the output hepfile, Dictionary of hepfile data

    Raises:
        InputError: If something is wrong with the specific input.
    """

    if outfile is None:
        outpath = csvpaths[0]
        outfile = outpath.replace(".csv", ".h5")

    if group_names is None:
        group_names = [os.path.split(file)[-1] for file in csvpaths]

    # organize into events
    csvs = {}
    for infile, group_name in zip(csvpaths, group_names):
        csv = pd.read_csv(infile)
        csvs[group_name] = csv

    return outfile, df_to_hepfile(
        csvs, outfile=outfile, event_num_col=common_key, write_hepfile=write_hepfile
    )
