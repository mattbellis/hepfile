import numpy as np
import sys
sys.path.append('../h5hep')
#from write import *
import hepfile

data = hepfile.initialize()

hepfile.create_group(data,'jet',counter='njet')
hepfile.create_dataset(data,['e','px','py','pz'],group='jet',dtype=float)

hepfile.create_group(data,'muons',counter='nmuon')
hepfile.create_dataset(data,['e','px','py','pz'],group='muons',dtype=float)

event = hepfile.create_single_event(data)

#'''
for i in range(0,1000):

    hepfile.clear_event(event)

    njet = 5
    event['jet/njet'] = njet

    for n in range(njet):
        event['jet/e'].append(np.random.random())
        event['jet/px'].append(np.random.random())
        event['jet/py'].append(np.random.random())
        event['jet/pz'].append(np.random.random())

    hepfile.pack(data,event)

print("Writing the file...")
#hdfile = hepfile.write_to_file('output.hdf5',data)
hdfile = hepfile.write_to_file('output.hdf5',data,comp_type='gzip',comp_opts=9)
#'''

