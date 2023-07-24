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
