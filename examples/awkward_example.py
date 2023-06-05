import numpy as np
import awkward as ak
import uproot as uproot

import sys

#from coffea.nanoevents import NanoEventsFactory, NanoAODSchema

import hepfile as hp


infilename = sys.argv[1]

#print("Reading in {0}".format(infilename))

#events = NanoEventsFactory.from_root(infilename, schemaclass=NanoAODSchema).events()
#print(len(events))

#:wq

data,event = np.load(infilename)
x = np.unpack_awkward_arrays(data,['jet'])



