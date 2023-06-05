Tutorial to write a hepfile
===========================

.. code:: ipython3

    # imports
    import numpy as np
    import sys
    
    from hepfile import write as writer

Once hepfile.write is imported, we need to start by initializing the
empty data structure.

.. code:: ipython3

    data = writer.initialize()

Now that the empty data structure is initialized, we must set up groups
and datasets. Groups hold datasets and datasets hold data about that
group. You can also just create higher level datasets that are
considered “singletons” which do not correspond to a specific group.

.. code:: ipython3

    # create the groups
    writer.create_group(data,'jet',counter='njet')
    writer.create_group(data,'muons',counter='nmuon')
    
    # add datasets to different groups
    writer.create_dataset(data,['e','px','py','pz'],group='jet',dtype=float)
    writer.create_dataset(data,['algorithm'],group='jet',dtype=int)
    writer.create_dataset(data,['words'],group='jet',dtype=str)
    writer.create_dataset(data,['e','px','py','pz'],group='muons',dtype=float)
    
    # add a higher level dataset that doesn't have a group, a "singleton"
    writer.create_dataset(data,['METpx','METpy'],dtype=float)

To start adding data to the groups and datasets we have to generate an
empty bucket.

.. code:: ipython3

    bucket = writer.create_single_bucket(data)

Now that we have the hepfile structure set up, we can generate random
data and insert it into the hepfile.

.. code:: ipython3

    rando_words = ["hi", "bye", "ciao", "aloha"]
    
    for i in range(0,10000):
    
        #hepfile.clear_event(event)
    
        njet = 17
        bucket['jet/njet'] = njet
    
        for n in range(njet):
            bucket['jet/e'].append(np.random.random())
            bucket['jet/px'].append(np.random.random())
            bucket['jet/py'].append(np.random.random())
            bucket['jet/pz'].append(np.random.random())
    
            bucket['jet/algorithm'].append(np.random.randint(-1,1))
    
            bucket['jet/words'].append(np.random.choice(rando_words))
    
        bucket['METpx'] = np.random.random()
        bucket['METpy'] = np.random.random()
    
        #hepfile.pack(data,event,EMPTY_OUT_BUCKET=False)
        return_value = writer.pack(data,bucket,STRICT_CHECKING=True)
        if return_value != 0:
            exit()

Finally, we are ready to write this random data to a file called
``output.hdf5``!

.. code:: ipython3

    print("Writing the file...")
    #hdfile = hepfile.write_to_file('output.hdf5',data)
    hdfile = writer.write_to_file('output.hdf5',data,comp_type='gzip',comp_opts=9,verbose=True)
