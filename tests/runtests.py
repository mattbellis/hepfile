import argparse
import os
import contextlib
import warnings
from inspect import getmembers, isfunction

import test_1_package
import test_2_read
import test_3_write
import test_4_awkward_tools
import test_5_dict_tools
import test_6_csv_tools

MODULES = [test_1_package,
           test_2_read,
           test_3_write,
           test_4_awkward_tools,
           test_5_dict_tools,
           test_6_csv_tools
           ]

if __name__ == '__main__':

    p = argparse.ArgumentParser()
    p.add_argument('--verbose', dest='verbose', action='store_true')
    p.add_argument('--debug', dest='debug', action='store_true')
    p.set_defaults(verbose=False)
    p.set_defaults(debug=False)
    args = p.parse_args()

    warnings.simplefilter("ignore") # suppress warnings

    # run all tests
    for module in MODULES:
        
        if args.verbose:
            print(f'\tRunning {module.__name__}')

        for func in getmembers(module, isfunction):

            # unpack func
            objname = func[0]
            obj = func[1]

            # call obj if it starts with test
            if objname[:4] == 'test':
                if args.verbose:
                    print(f'\t\tRunning {objname}')

                if args.debug:
                    obj()
                else:
                    with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
                        obj()
