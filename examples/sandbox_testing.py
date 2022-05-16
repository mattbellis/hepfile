import numpy as np
import sys
#import hepfile

# For development
sys.path.append('../src/hepfile')
import write as hepfile

data = hepfile.initialize()

hepfile.create_group(data,'jet')#,counter='njet')

