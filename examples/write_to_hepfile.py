import numpy as np
import sys
import hepfile

# For development
#sys.path.append('../src/hepfile')
#import write as hepfile

data = hepfile.initialize()

hepfile.create_group(data,'jet',counter='njet')
hepfile.create_dataset(data,['e','px','py','pz'],group='jet',dtype=float)
hepfile.create_dataset(data,['algorithm'],group='jet',dtype=int)
hepfile.create_dataset(data,['words'],group='jet',dtype=str)

hepfile.create_group(data,'muons',counter='nmuon')
hepfile.create_dataset(data,['e','px','py','pz'],group='muons',dtype=float)

event = hepfile.create_single_event(data)

rando_words = ["hi", "bye", "ciao", "aloha"]

#'''
for i in range(0,10000):

    hepfile.clear_event(event)

    njet = 5
    event['jet/njet'] = njet

    for n in range(njet):
        event['jet/e'].append(np.random.random())
        event['jet/px'].append(np.random.random())
        event['jet/py'].append(np.random.random())
        event['jet/pz'].append(np.random.random())

        event['jet/algorithm'].append(np.random.randint(-1,1))

        event['jet/words'].append(np.random.choice(rando_words))

    hepfile.pack(data,event)

print("Writing the file...")
#hdfile = hepfile.write_to_file('output.hdf5',data)
hdfile = hepfile.write_to_file('output.hdf5',data,comp_type='gzip',comp_opts=9,verbose=True)
#'''

