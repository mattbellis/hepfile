import numpy as np
import sys
import hepfile

#sys.path.append("../hepfile")
#sys.path.append("../src/hepfile")
#import write as hepfile


def write_file_for_unit_tests():
    data = hepfile.initialize()

    hepfile.create_group(data, "jet", counter="njet")
    hepfile.create_dataset(data, ["e", "px", "py", "pz"], group="jet", dtype=float)

    hepfile.create_group(data, "muons", counter="nmuon")
    hepfile.create_dataset(data, ["e", "px", "py", "pz"], group="muons", dtype=float)

    hepfile.create_dataset(data, ["METpx", "METpy"], dtype=float)

    event = hepfile.create_single_event(data)

    #'''
    for i in range(0, 10):

        #hepfile.clear_event(event)

        njet = 5
        event["jet/njet"] = njet

        for n in range(njet):
            event["jet/e"].append(np.random.random())
            event["jet/px"].append(np.random.random())
            event["jet/py"].append(np.random.random())
            event["jet/pz"].append(np.random.random())

        event['METpx'] = np.random.random()
        event['METpy'] = np.random.random()

        hepfile.pack(data, event)

    print("Writing the file...")
    # hdfile = write_to_file('output.hdf5',data)
    hdfile = hepfile.write_to_file("FOR_TESTS.hdf5", data, comp_type="gzip", comp_opts=9)
    #'''


if __name__ == "__main__":
    write_file_for_unit_tests()
