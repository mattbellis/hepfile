import numpy as np
import awkward1 as ak
import uproot4 as uproot

import sys

from coffea.nanoevents import NanoEventsFactory, NanoAODSchema

import h5hep as hp


infilename = sys.argv[1]

print("Reading in {0}".format(infilename))

events = NanoEventsFactory.from_root(infilename, schemaclass=NanoAODSchema).events()
print(len(events))

:wq


