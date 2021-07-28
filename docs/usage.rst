======
Usage
======

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





