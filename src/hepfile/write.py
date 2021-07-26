import numpy as np
import h5py as h5
import datetime
import sys
import hepfile


################################################################################
def initialize():

    """ Creates an empty data dictionary

    Returns:

	**data** (dict): An empty data dictionary

    """

    data = {}
    data["groups"] = {}
    data["datasets_and_counters"] = {}
    data["list_of_counters"] = []

    # For singleton entries, variables with only one entry per event.
    data["groups"]["_SINGLETON_"] = ["INDEX"]
    data["datasets_and_counters"]["_SINGLETON_"] = "_SINGLETON_/INDEX"
    data["list_of_counters"].append("_SINGLETON_/INDEX")

    data["_SINGLETON_/INDEX"] = []
    data["dataset_data_types"] = {}
    data["dataset_data_types"]["_SINGLETON_/INDEX"] = int

    data["_PROTECTED_NAMES_"] = ["_PROTCTED_NAMES_", \
            "groups", \
            "datasets_and_counters", \
            "list_of_counters", \
            "_SINGLETON_/INDEX", \
            "dataset_data_types"]

    return data


################################################################################
def clear_event(event):

    """ Clears the data from the event dictionary - should the name of the function change?

    Args:
	**event** (dict): The dictionary to be cleared. This is designed to clear the data from
                      the lists in the **event** dictionary, but theoretically, it would
                      clear out the lists from any dictionary. 

    """

    for key in event.keys():
        if type(event[key]) == list:
            event[key].clear()

        #'''
        # Is this the right thing to do here?????
        elif type(event[key]) == int:
            event[key] = 0
        elif type(event[key]) == float:
            event[key] = 0.0
        #'''


################################################################################
# Create a single event (dictionary) that will eventually be used to fill
# the overall dataset
################################################################################
def create_single_event(data):

    """ Creates an event dictionary that will be used to collect data and then
    packed into the the master data dictionary.

    Args:
	**data** (dict): Data dictionary that will hold all the data from the events.

    Returns:
	**event** (dict): The new event dictionary with keys and no event information

    """

    event = {}

    for k in data.keys():
        ### IS THIS FIRST ONE DEPRECATED FOR SOME EARLIER DEV CYCLE???
        if k[-5:] == "index":
            event[k] = data[k]
        elif k in data["groups"]["_SINGLETON_"]:
            event[k] = None
        elif k in data["list_of_counters"]:
            event[k] = 0
        else:
            event[k] = data[k].copy()

    return event


################################################################################
# This adds a group in the dictionary, similar to
# a la CreateBranch in ROOT
################################################################################
def create_group(data, groupname, counter=None):

    """ Adds a group in the dictionary

    Args:
	**data** (dict): Dictionary to which the group will be added

	**groupname** (string): Name of the group to be added

	**counter** (string): Name of the counter key. None by default

    """

    keys = data.keys()

    # Put the counter in the dictionary first.
    """
    if counter is not None:
        data['datasets_and_counters'][groupname] = counter
        keyfound = False
        for k in keys:
            if counter == k:
                keyfound = True
        if keyfound == False:
            data[counter] = []
    """

    # Then put the group and any datasets in there next.
    keyfound = False
    for k in keys:
        if groupname == k:
            print("\033[1m%s\033[0m is already in the dictionary!" % (groupname))
            keyfound = True
            break
    if keyfound == False:
        # data[groupname] = []
        data["groups"][groupname] = []
        print("Adding group \033[1m%s\033[0m" % (groupname))
        if counter is not None:
            data["groups"][groupname].append(counter)
            name = "%s/%s" % (groupname, counter)
            # data['datasets_and_counters'][groupname] = counter
            data["datasets_and_counters"][groupname] = name
            data["dataset_data_types"][name] = int
            if name not in data["list_of_counters"]:
                data["list_of_counters"].append(name)
            data[name] = []
            print(
                "Adding a counter for \033[1m%s\033[0m as \033[1m%s\033[0m"
                % (groupname, counter)
            )
        else:
            print("----------------------------------------------------")
            print("There is no counter to go with group \033[1m%s\033[0m" % (groupname))
            print("Are you sure that's what you want?")
            print("-----------------------------------------------------")


################################################################################
# This adds a dataset to the dictionary, similar to
# a la CreateBranch in ROOT
# 
# This can also add a dataset that is not associate with a group
################################################################################
def create_dataset(data, datasets, group=None, dtype=None):

    """ Adds a dataset to a group in a dictionary. If the group does not exist, it will be created.

    Args:
	**data** (dict): Dictionary that contains the group
	
	**datasets** (list): Dataset to be added to the group (This doesn't have to be a list)

	**group** (string): Name of group the dataset will be added to.  None by default

	**dtype** (type): The data type. None by default - I don't think this is every used 

    Returns:
	**-1**: If the group is None


    """

    keys = data.keys()

    if group is None:
        print("-----------------------------------------------")
        print("You need to assign this dataset(s) to a group!")
        print("Groups are not added")
        print("-----------------------------------------------")

        if type(datasets) != list:
            datasets = [datasets]

        for dataset in datasets:
            keyfound = False
            for k in data["groups"]["_SINGLETON_"]:
                if dataset == k:
                    print("\033[1m%s\033[0m is already in the dictionary!" % (dataset))
                    keyfound = True
            if keyfound == False:
                print(
                    "Adding dataset \033[1m%s\033[0m to the dictionary as a SINGLETON."
                    % (dataset)
                )
                data["groups"]["_SINGLETON_"].append(dataset)
                data[dataset] = []
                # counter_name = "%s/%s" % (group,counter)
                data["datasets_and_counters"][dataset] = "_SINGLETON_/INDEX"

                data["dataset_data_types"][dataset] = dtype

        return 0

    # Put the counter in the dictionary first.
    keyfound = False
    for k in data["groups"]:
        if group == k:
            keyfound = True

    # NEED TO FIX THIS PART SO THAT IT FINDS THE RIGHT COUNTER FROM THE GROUP
    if keyfound == False:
        print("Your group, \033[1m%s\033[0m is not in the dictionary yet!" % (group))
        counter = "n%s" % (group)
        print("Adding it, along with a counter of \033[1m%s\033[0m" % (counter))
        create_group(data, group, counter=counter)

    # Then put the datasets into the group in there next.
    if type(datasets) != list:
        datasets = [datasets]

    for dataset in datasets:
        keyfound = False
        name = "%s/%s" % (group, dataset)
        for k in keys:
            if name == k:
                print("\033[1m%s\033[0m is already in the dictionary!" % (name))
                keyfound = True
        if keyfound == False:
            print(
                "Adding dataset \033[1m%s\033[0m to the dictionary under group \033[1m%s\033[0m."
                % (dataset, group)
            )
            data[name] = []
            data["groups"][group].append(dataset)

            # Add a counter for this dataset for the group with which it is associated.
            counter = data["datasets_and_counters"][group]
            # counter_name = "%s/%s" % (group,counter)
            data["datasets_and_counters"][name] = counter

            data["dataset_data_types"][name] = dtype

    return 0


################################################################################
def pack(data, event, EMPTY_OUT_EVENT_BUCKET=True):

    """ Takes the data from an event and packs it into the data dictionary, 
    intelligently, so that it can be stored and extracted efficiently. 
    (This is analagous to the ROOT TTree::Fill() member function).

    Args:
	**data** (dict): Data dictionary to hold the entire dataset EDIT.

	**event** (dict): Event to be packed into data.

	**EMPTY_OUT_EVENT_BUCKET** (bool): If this is `True` then empty out the `event`
				container in preparation for the next iteration. We used to ask the users to do
				this "by hand" but now do it automatically by default. We allow the user to 
				not do this, if they are running some sort of debugging. 

    """

    keys = list(event.keys())

    for key in keys:
        # print(key)

        if (
            key == "datasets_and_counters"
            or key == "groups"
            or key == "list_of_counters"
            or key == "dataset_data_types"
        ):
            continue

        # The singletons will only have 1 entry per event
        if key == "_SINGLETON_/INDEX":
            data[key].append(1)
            continue

        # if key[-5:] == 'counter':
        # continue
        if type(event[key]) == list:
            value = event[key]
            if len(value) > 0:
                data[key] += value
            """
            else:
                # No entries for this event
                #print(key)
                counter = data['datasets_and_counters'][key]
                data[counter].append(0)
                if counter in keys:
                    keys.remove(counter)
            """
        else:
            # This is for counters and SINGLETONS
            if key in data["groups"]["_SINGLETON_"]:
                if event[key] == None:
                    print(
                        "\n\033[1m%s\033[0m is part of the SINGLETON group and is expected to have a value for each event."
                        % (key)
                    )
                    print("However it is None...exiting.\n")
                    exit()
            else:
                data[key].append(event[key])

    # Clear out the event after it's been packed if that's what we want
    if EMPTY_OUT_EVENT_BUCKET:
        clear_event(event)

################################################################################
def convert_list_and_key_to_string_data(datalist, key):

    """ Converts data dictionary to a string

    Args:
	**datalist** (list): A list to be saved as a string.

    Returns:
	**key** (string): We will assume that this will be unpacked as a dictionary,
                      and this will be the key for the list in that dictionary.

    """

    a = np.string_(key)

    mydataset = []
    b = np.string_("")
    nvals = len(datalist)
    for i, val in enumerate(datalist):
        # print(val,type(val))
        b += np.string_(val)
        if i < nvals - 1:
            b += np.string_("__:__")
    mydataset.append([a, b])

    return mydataset


################################################################################

################################################################################
def convert_dict_to_string_data(dictionary):

    """ Converts data dictionary to a string

    Args:
	**dictionary** (dict): Dictionary to be converted to a string

    Returns:
	**mydataset** (string): String representation of the dataset

    """

    keys = dictionary.keys()

    nkeys = len(keys)

    mydataset = []
    for i, key in enumerate(keys):
        # print(i,key,dictionary[key])
        a = np.string_(key)
        b = np.string_(dictionary[key])
        mydataset.append([a, b])

    return mydataset


################################################################################
# This function writes default attributes and metadata to a file.
################################################################################
def write_file_metadata(filename, mydict={}, write_default_values=True, append=True):
    """ Writes file metadata in the attributes of an HDF5 file

    Args:
    **filename** (string): Name of output file

    **mydict** (dictionary): Metadata desired by user

    **write_default_values** (boolean): True if user wants to write/update the 
                                        default metadata: date, hepfile version, 
                                        h5py version, numpy version, and Python 
                                        version, false if otherwise.

    **append** (boolean): True if user wants to keep older metadata, false otherwise.

    Returns:
    **hdoutfile** (HDF5): File with new metadata

    """

    hdoutfile = h5.File(filename, "a")

    non_metadata = ["nentries"]

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
    filename, data, comp_type=None, comp_opts=None, force_single_precision=True,  verbose=False
):

    """ Writes the selected data to an HDF5 file

    Args:
	**filename** (string): Name of output file

	**data** (dictionary): Data to be written into output file

	**comp_type** (string): Type of compression

	**force_single_precision** (boolean): True if data should be written in single precision

    Returns:
	**hdoutfile** (HDF5): File to which the data has been written 

    """

    hdoutfile = h5.File(filename, "w")

    groups = data["groups"].keys()

    # Convert this to a 2xN array for writing to the hdf5 file.
    # This gives us one small list of informtion if we need to pull out
    # small chunks of data
    mydataset = convert_dict_to_string_data(data["datasets_and_counters"])
    dset = hdoutfile.create_dataset(
        "datasets_and_counters",
        data=mydataset,
        dtype="S256",
        compression=comp_type,
        compression_opts=comp_opts,
    )

    # Convert this to a 2xN array for writing to the hdf5 file.
    # This has the groups and the datasets in them.
    mydataset = convert_list_and_key_to_string_data(
        data["groups"]["_SINGLETON_"], "_SINGLETONGROUP_"
    )
    dset = hdoutfile.create_dataset(
        "_SINGLETONGROUP_",
        data=mydataset,
        dtype="S256",
        compression=comp_type,
        compression_opts=comp_opts,
    )

    for group in groups:

        # print(group)

        hdoutfile.create_group(group)
        hdoutfile[group].attrs["counter"] = np.string_(
            data["datasets_and_counters"][group]
        )

        datasets = data["groups"][group]

        # print(datasets)

        for dataset in datasets:

            name = None
            if group == "_SINGLETON_" and dataset is not "INDEX":
                name = dataset
            else:
                name = "%s/%s" % (group, dataset)

            x = data[name]

            dataset_dtype = data['dataset_data_types'][name]
            #print(dataset_dtype)


            if type(x) == list:
                x = np.array(x)

            # Do single precision only, unless specified
            if force_single_precision == True:
                if x.dtype == np.float64:
                    x = x.astype(np.float32)
                    dataset_dtype = np.float32

            if dataset_dtype is not str:
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
                arr = np.array(x,dtype='S'+str(longest_word))
                hdoutfile.create_dataset(name, data=arr, dtype=dataset_dtype,  compression=comp_type, compression_opts=comp_opts)


            if (verbose):
                print(f"Writing to file {name} as type {str(dataset_dtype)}")
                   

    # Get the number of events
    counters = data["list_of_counters"]
    nentries = -1
    prevcounter = None
    for i, countername in enumerate(counters):
        ncounter = len(data[countername])
        print("%-32s has %-12d entries" % (countername, ncounter))
        if i > 0 and ncounter != nentries:
            print("-------- WARNING -----------")
            print(
                "%s and %s have differing numbers of entries!"
                % (countername, prevcounter)
            )
            print("-------- WARNING -----------")
            # SHOULD WE EXIT ON THIS?

        if nentries < ncounter:
            nentries = ncounter

        prevcounter = countername

    hdoutfile.attrs["nentries"] = nentries
    hdoutfile.close()

    write_file_metadata(filename)

    return hdoutfile
