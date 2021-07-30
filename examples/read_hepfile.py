import numpy as np
import matplotlib.pylab as plt
import time

#import hepfile

import sys

sys.path.append('../src/hepfile')
import read as hepfile


filename = sys.argv[1]

#data,event = hepfile.load(filename,subset=(0,100000))
#data,event = hepfile.load(filename,verbose=False)#,subset=10000)
#data,event = hepfile.load(filename,desired_datasets=['jet','muon'])
#data,event = hepfile.load(filename,desired_datasets=['jet'])
data,event = hepfile.load(filename,desired_datasets=['jet'],subset=(5,10))
#data,event = hepfile.load(filename,desired_datasets=['jet','muon'],subset=(0,100000))

if data is None:
    print("Exiting...")
    exit()

#print(data['list_of_counters'])

nbuckets_in_file = hepfile.get_nbuckets_in_file(filename)
print("nentries in file: ",nbuckets_in_file)

nbuckets = hepfile.get_nbuckets_in_data(data)
print("nentries: ",nbuckets)

#print(type(data),type(event))

energies = []

#print("A")
#print(data.keys())
#print(data)
#
#print("B")
#print(event.keys())
#print(event)
#x = data['jet/e']

# Print out what has been read in from the files.
'''
for key in event.keys():
    print(key)
'''

for i in range(0,nbuckets):

    if i%10000==0:
        print(i)

    hepfile.unpack(event,data,n=i)

    #print(event['jet/njet'])

    energy = event['jet/e']

    '''
    for e in energy:
        energies.append(e)
    '''
    energies += energy.tolist()


print(len(energies))

plt.figure()
plt.hist(energies,bins=100,range=(0,500))

#plt.show()
