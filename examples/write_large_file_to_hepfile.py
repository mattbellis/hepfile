import numpy as np
from numpy.random import beta
import sys
#sys.path.append('../h5hep')
#from write import *
import hepfile

################################################################################
def calc_energy(mass,px,py,pz):

    energy = np.sqrt(mass*mass + px*px + py*py + pz*pz)

    return energy

################################################################################

data = hepfile.initialize()

hepfile.create_group(data,'jet',counter='njet')
hepfile.create_dataset(data,['e','px','py','pz','btag'],group='jet',dtype=float)

hepfile.create_group(data,'muon',counter='nmuon')
hepfile.create_dataset(data,['e','px','py','pz','q'],group='muon',dtype=float)

hepfile.create_group(data,'electron',counter='nelectron')
hepfile.create_dataset(data,['e','px','py','pz','q'],group='electron',dtype=float)

hepfile.create_group(data,'photon',counter='nphoton')
hepfile.create_dataset(data,['e','px','py','pz'],group='photon',dtype=float)

hepfile.create_group(data,'MET',counter='nMET')
hepfile.create_dataset(data,['pt','phi'],group='MET',dtype=float)

event = hepfile.create_single_bucket(data)

nentries = 10000

#print(data)
#print(event)

#'''
for i in range(0,nentries):

    if i%1000==0:
        print(i)

    njet = np.random.randint(10)
    event['jet/njet'] = njet
    for n in range(njet):
        px = 300*beta(2,9)
        py = 300*beta(2,9)
        pz = 300*beta(2,9)
        mass = 5*beta(2,9)
        energy = calc_energy(mass,px,py,pz)
        event['jet/px'].append(px)
        event['jet/py'].append(py)
        event['jet/pz'].append(pz)
        event['jet/e'].append(energy)
        event['jet/btag'].append(np.random.random())

    nmuon = np.random.randint(10)
    event['muon/nmuon'] = nmuon
    for n in range(nmuon):
        px = 300*beta(2,9)
        py = 300*beta(2,9)
        pz = 300*beta(2,9)
        mass = 0.105
        energy = calc_energy(mass,px,py,pz)
        event['muon/px'].append(px)
        event['muon/py'].append(py)
        event['muon/pz'].append(pz)
        event['muon/e'].append(energy)
        event['muon/q'].append(2*np.random.randint(2) - 1)

    nelectron = np.random.randint(10)
    event['electron/nelectron'] = nelectron
    for n in range(nelectron):
        px = 300*beta(2,9)
        py = 300*beta(2,9)
        pz = 300*beta(2,9)
        mass = 0.000511
        energy = calc_energy(mass,px,py,pz)
        event['electron/px'].append(px)
        event['electron/py'].append(py)
        event['electron/pz'].append(pz)
        event['electron/e'].append(energy)
        event['electron/q'].append(2*np.random.randint(2) - 1)

    nphoton = np.random.randint(10)
    event['photon/nphoton'] = nphoton
    for n in range(nphoton):
        px = 300*beta(2,9)
        py = 300*beta(2,9)
        pz = 300*beta(2,9)
        mass = 0.0
        energy = calc_energy(mass,px,py,pz)
        event['photon/px'].append(px)
        event['photon/py'].append(py)
        event['photon/pz'].append(pz)
        event['photon/e'].append(energy)
        
    hepfile.pack(data,event)

print("Writing the file...")
#hdfile = write_to_file('output.hdf5',data)
hdfile = hepfile.write_to_file('HEP_random_file_LARGE.hdf5',data,comp_type='gzip',comp_opts=9)
#'''

