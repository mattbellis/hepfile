======
Usage
======

Writing data
------------

Initialize the `data` dictionary
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To create the `data` dictionary, run ::

    my_data = hepfile.initialize()

Create groups
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To create groups, run ::

    hepfile.create_group(my_data, 'my_group', counter = 'my_counter')

with whatever name is desired replacing ``'my_group'`` and ``'my_counter'``. Be aware
that if nothing is set for ``counter =`` , hepfile will set ``'N_' + 'my_group'`` (or its replacement)
as the counter.

DTYPE .....

Create datasets for those groups
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To create a dataset inside of ``'my_group'``, run ::

    hepfile.create_groups()

Create a single bucket dictionary
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Loop over data and pack the buckets as you go
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Write the data to file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^




Reading data
------------

Load in the data
^^^^^^^^^^^^^^^^

Show how subsets and desired datasets can be used.

Loop over the data and unpack each bucket
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^




HEP Example
-------------

Here we will go through the steps involved in analyzing HEP data pulled from an HDF5
file, and creating a file of random data using hepfile functions. As an example, we
will be calculating (insert something to )

Reading Data with hepfile
--------------------------

We begin with a file, and load it into an empty data dictionary::

    data, event = hepfile.load(infile)

*data* is a dictionary containing counters, indices, and data for all the
features we care about. *event* is an empty dictionary waiting to be filled by
data from some specific event.

    


Writing Data with hepfile
---------------------------


Adding Metadata with hepfile
-----------------------------





