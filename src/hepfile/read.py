import h5py as h5
import numpy as np

################################################################################
def load(filename=None, verbose=False, desired_datasets=None, subset=None):

    '''
    Reads all, or a subset of the data, from the HDF5 file to fill a data dictionary.
    Returns an empty dictionary to be filled later with select events.

    Args:
	**filename** (string): Name of the input file
	
	**verbose** (boolean): True if debug output is required

	**desired_datasets** (list): Datasets to be read from input file

	**subset** (int): Number of events to be read from input file

    Returns:
	**ourdata** (dict): Selected data from HDF5 file
	
	**event** (dict): An empty event dictionary to be filled by individual events

    '''

    f = None
    if filename != None:
        f = h5.File(filename, "r+")
    else:
        print("No filename passed in! Can't open file.\n")
        return None

    ourdata = {}
    ourdata["_MAP_DATASETS_TO_COUNTERS_"] = {}
    ourdata["_MAP_DATASETS_TO_INDEX_"] = {}
    ourdata["_LIST_OF_COUNTERS_"] = []
    ourdata["_LIST_OF_DATASETS_"] = []

    ourdata["_NUMBER_OF_BUCKETS_"] = f.attrs["_NUMBER_OF_BUCKETS_"]
    if subset is not None:
        if type(subset) == int:
            subset = (0, subset)
        ourdata["_NUMBER_OF_BUCKETS_"] = subset[1] - subset[0]

    event = {}

    # Get the datasets and counters
    dc = f["_MAP_DATASETS_TO_COUNTERS_"]
    for vals in dc:
        # The decode is there because vals were stored as numpy.bytes
        counter = vals[1].decode()
        index = "%s_INDEX" % (counter)
        ourdata["_MAP_DATASETS_TO_COUNTERS_"][vals[0].decode()] = counter
        ourdata["_MAP_DATASETS_TO_INDEX_"][vals[0].decode()] = index
        ourdata["_LIST_OF_COUNTERS_"].append(vals[1].decode())
        ourdata["_LIST_OF_DATASETS_"].append(vals[0].decode())
        ourdata["_LIST_OF_DATASETS_"].append(vals[1].decode())  # Get the counters as well

    # We may have added some strings (like counters) multiple times.
    ourdata["_LIST_OF_COUNTERS_"] = np.unique(ourdata["_LIST_OF_COUNTERS_"]).tolist()
    ourdata["_LIST_OF_DATASETS_"] = np.unique(ourdata["_LIST_OF_DATASETS_"]).tolist()

    # Pull out the SINGLETON datasets
    sg = f["_SINGLETONGROUP_"][0]  # This is a numpy array of strings
    decoded_string = sg[1].decode()

    vals = decoded_string.split("__:__")
    vals.remove("COUNTER")

    ourdata["_SINGLETONS_GROUP_"] = vals

    # Get the list of datasets and groups, but remove the
    # '_MAP_DATASETS_TO_COUNTERS_', as that is a protected key.
    entries = ourdata["_LIST_OF_DATASETS_"]

    ########################################################
    # Only keep select data from file
    ########################################################
    if desired_datasets is not None:
        if type(desired_datasets) != list:
            desired_datasets = list(desired_datasets)

        # Count backwards because we'll be removing stuff as we go.
        i = len(entries) - 1
        while i >= 0:
            entry = entries[i]

            is_dropped = True
            for desdat in desired_datasets:
                if desdat in entry:
                    is_dropped = False
                    break

            if is_dropped == True:
                print("Not reading out %s from the file...." % (entry))
                entries.remove(entry)

            i -= 1
    #######################################################

    if verbose == True:
        print("Datasets and counters:")
        print(ourdata["_MAP_DATASETS_TO_COUNTERS_"])
        print("\nDatasets and indices:")
        print(ourdata["_LIST_OF_COUNTERS_"])

    # Pull out the counters first and build the indices
    print("Building the indices...")
    for name in ourdata["_LIST_OF_COUNTERS_"]:
        if subset is not None:
            ourdata[name] = f[name][subset[0] : subset[1]]
        else:
            ourdata[name] = f[name][:]

        # counter = f[name].value
        indexname = "%s_INDEX" % (name)
        index = np.zeros(len(ourdata[name]), dtype=int)
        start = 0
        _NUMBER_OF_BUCKETS_ = len(index)
        for i in range(0, _NUMBER_OF_BUCKETS_):
            index[i] = start
            nobjs = ourdata[name][i]
            start = index[i] + nobjs
        ourdata[indexname] = index
    print("Built the indices!")

    # Loop over the entries we want and pull out the data.
    for name in entries:

        # The decode is there because counter is a numpy.bytes object
        counter = None
        if name not in ourdata["_LIST_OF_COUNTERS_"]:
            counter = ourdata["_MAP_DATASETS_TO_COUNTERS_"][name]

        if verbose == True:
            print(f[name])

        data = f[name]
        # for data in f[name]:
        if type(data) == h5.Dataset:
            datasetname = name

            if subset is not None:
                ourdata[datasetname] = data[subset[0] : subset[1]]
            else:
                ourdata[datasetname] = data[:]

            event[datasetname] = None  # This will be filled for individual events
            if verbose == True:
                print(data)

    f.close()
    print("Data is read in and input file is closed.")

    return ourdata, event


################################################################################


################################################################################
def unpack(event, data, n=0):

    """ Fills the event dictionary with selected events.

    Args:

	**event** (dict): Event dictionary to be filled

	**data** (dict): Data dictionary used to fill the event dictionary

    """

    keys = event.keys()

    for key in keys:

        # if "num" in key:
        # IS THERE A WAY THAT THIS COULD BE FASTER?
        # print(data['_LIST_OF_COUNTERS_'],key)
        if key in data["_LIST_OF_COUNTERS_"] or key in data["_SINGLETONS_GROUP_"]:
            # print("here! ",key)
            event[key] = data[key][n]

        elif "INDEX" not in key:  # and 'Jets' in key:
            indexkey = data["_MAP_DATASETS_TO_INDEX_"][key]
            numkey = data["_MAP_DATASETS_TO_COUNTERS_"][key]

            if len(data[indexkey]) > 0:
                index = data[indexkey][n]

            if len(data[numkey]) > 0:
                nobjs = data[numkey][n]
                event[key] = data[key][index : index + nobjs]


################################################################################
def get_nbuckets(filename):

    """ Get the number of entries in the file.

    """

    f = h5.File(filename, "r+")

    a = f.attrs

    if a.__contains__("_NUMBER_OF_BUCKETS_"):
        _NUMBER_OF_BUCKETS_ = a.get("_NUMBER_OF_BUCKETS_")
        f.close()
        return _NUMBER_OF_BUCKETS_
    else:
        print('\nFile does not contain the attribute, "_NUMBER_OF_BUCKETS_"\n')
        f.close()
        return None


################################################################################
def get_file_metadata(filename):

    """ Get the file metadata and return it as a dictionary

    """

    f = h5.File(filename, "r+")

    a = f.attrs

    if len(a) < 1:
        print(f"No metadata in file {filename}!")
        print(f"File has no attributes.\n")
        f.close()
        return None

    metadata = {}

    for key in a.keys():
        metadata[key] = a[key]

    f.close()

    return metadata


################################################################################

################################################################################
def print_file_metadata(filename):

    """ Pretty print the file metadata 

    """

    metadata = get_file_metadata(filename)

    if metadata is None:
        return None

    output = ""

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
