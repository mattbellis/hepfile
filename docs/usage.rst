p======
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

Be aware that if nothing is set for ``counter =`` , hepfile will set ``'N_' + '{group_name}'`` 
(or its replacement) as the counter.


Create datasets for those groups
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To create a dataset inside of ``'my_group'``, run ::

    hepfile.create_dataset(my_data, 'my_dataset', group = 'my_group', dtype = str)

If nothing is set for ``group =``, then the dataset created will be put into the 
_SINGLETONS_GROUP_, as shown below ::

    hepfile.create_dataset(my_data, 'my_unique', dtype = int)

If nothing is set for ``dtype =``, then it will be assumed that
the dataset is storing floats. This will cause problems when writing the data to the
HDF5 file, so make sure to set the dataset type correctly. Dataset types cannot be
changed after the fact.

An additional feature for convenience is that multiple datasets in the same group
and of the same type can be created at the same time by inputting a list of names
instead of a single dataset name, like so: ::

    hepfile.create_dataset(my_data, ['data1', 'data2'] , group = 'my_group')

Create a single bucket dictionary
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To create a bucket dictionary with the same structure as the overall data dictionary,
run ::

    my_bucket = hepfile.create_single_bucket(my_data)

Note that the entire structure of the data dictionary must be finalized, since 
any additional datasets or groups created in ``my_data`` will not be reflected
in ``my_bucket``.

Loop over data and pack the buckets as you go
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An example of writing data into a bucket and then packing it into a data dictionary
is shown below ::
    
    for i in range(5)
        my_bucket['my_group/my_dataset'] = 'yes'
        my_bucket['my_group/data1'] = 1.0
        my_bucket['my_group/data2'] = 2.0
        
    my_bucket['my_unique'] = 3

    hepfile.pack(my_data, my_bucket)

Unlike in ROOT, there is no need to set the group counter at all! hepfile does so
automatically, looking at the first non-counter dataset in each group and setting the 
group counter for that bucket to be the length of the bucket's dataset. This is unlike
ROOT, and would take some cycles, so this can be turned off by setting 
``AUTO_SET_COUNTER`` to ``False``. Simply replace the last line of the previous codeblock
with the following to demonstrate: ::

    my_bucket['my_group/my_counter'] = 5
    hepfile.pack(my_data, my_bucket, AUTO_SET_COUNTER = False)

Note that the flag must be set to false, or anything you put for the counter will
be overwritten. 

If for debugging/peace of mind, you want to make sure that all datasets
belonging to one group in the bucket are the same length, simply set the ``STRICT_CHECKING``
flag to ``True``. If you were to run the following code where two datasets in ``my_group`` have
different lengths, pack would not update the data dictionary and would warn the user
about their mistake: ::

    for i in range(5)
        my_bucket['my_group/my_dataset'].append('yes')
        my_bucket['my_group/data1'].append(1.0)
        my_bucket['my_group/data1'].append(1.5)
        my_bucket['my_group/data2'].append(2.0)
        
    my_bucket['my_unique'] = 3

    hepfile.pack(my_data, my_bucket, STRICT_CHECKING = True)

Normally, pack clears the bucket after writing the data to the data dictionary.
To remove this behavior for debugging purposes, set the flag ``EMPTY_OUT_BUCKET``
to ``False``. The following two lines are equivalent to ``hepfile.pack(my_data, my_bucket)`` ::

    hepfile.pack(my_data, my_bucket, EMPTY_OUT_BUCKET = False)
    hepfile.clear_bucket(my_bucket)

Finally, if you want to look at the structure of the bucket dictionary while packing it,
you can set the ``verbose`` flag to ``True``. Note that this will have no effect
unless ``AUTO_SET_COUNTER`` is left untouched or is set to ``True``.


Write the data to file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To write the data dictionary to a file, run ::

    hepfile.write_to_file('my_file.hdf5', my_data)

Note that the data dictionary must be complete, as you cannot edit the file
once it has been created.

MORE FLAGS?

Write metadata to file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On execution of ``write_to_file``, some metadata will automatically be
be written to the file. This will include the date the file is created and
the version numbers of hepfile, numpy, h5py, and python used while creating
the file. If more metadata is needed, it can be added with the following
line of code: ::

    hepfile.write_file_metadata('my_file.hdf5', mydict = {'author':'John Doe'})

Due to limitations placed on hepfile by h5py, only 60k bytes of metadata
can be added into the attributes of a HDF5 file.

If you do not want hepfile to rewrite the default metadata while adding your
own, you can set the flag ``write_default_values`` to ``False`` like so: ::

    hepfile.write_file_metadata('my_file.hdf5', mydict = {'author': 'John Doe'},
                                write_default_values = False)

If you want to delete all existing metadata from an HDF5 file, you can set the
flag ``append`` to ``False``. Note that this will delete the default metadata
as well, so it must be added again. This can be done by passing in nothing
for ``mydict`` and either setting ``write_default_values`` to ``True`` or leaving
it unchanged. An example is shown below: ::

    hepfile.write_file_metadata('my_file.hdf5', mydict = {'author': 'John Doe'}, append = False)
    hepfile.write_file_metadata('my_file.hdf5')


Reading data
------------

Load in the data
^^^^^^^^^^^^^^^^

To load the data in from the file ``my_file.hdf5``, run ::

    data, bucket = hepfile.load('my_file.hdf5')

``data`` is a dictionary with all the data from the file (organized in 
the hepfile schema), and ``bucket`` is an empty dictionary with the same
structure ready to be filled with specific buckets from ``data``.

Let's say you want to only see the datasets *my_unique* and *data1*.
We can limit memory use by only pulling in these datasets from the file
using the ``desired_datasets`` variable. Simply call ::

    data, bucket = hepfile.load('my_file.hdf5', desired_datasets = ['my_unique', 'data1'])

``data`` and ``bucket`` will contain the datasets (empty or not) *'my_unique'* and
*'my_group/data1'*. Note that desired_datasets works on the basis of string matching:
only putting in 'data' would extract both *'my_group/data1'* and *'my_group/data2'*.
To extract some specific group, putting in the group name will work, since
``'my_group' in 'my_group/my_dataset' == True``, as well as any other dataset in it.


Additionally, the file may contain more expansive ranges of data than you want to
analyze. In this case, simply set the subset variable equal to the range of bucket
counters you want to study. For example, if you cared about buckets 2-5, you would run ::

    data, bucket = hepfile.load('my_file.hdf5', subset = [2,5])

Additionally, if you want to load in the first *N* buckets, you could run ::

    data, bucket = hepfile.load('my_file.hdf5', subset = N)

If *N* is greater than the total number of buckets, the upper range will be set at
the last bucket in the data file. 

Loop over the data and unpack each bucket
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^




