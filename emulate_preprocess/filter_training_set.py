
# Imports
#import sys
import numpy as np
import os
import sys
import copy
import pickle

#special change, add yourself to sys.path to call scope.
mydir = os.path.dirname( os.path.realpath( __file__ ) )
sys.path.append( mydir )

import context
from fourdvar.util.emulate_input_struct import EmulationInput
import emulate_preprocess.training_defn as training_defn

with open(training_defn.train_input_raw_fname,'rb') as f:
    input_src = pickle.load(f)
with open(training_defn.train_output_raw_fname,'rb') as f:
    output_src = pickle.load(f)

output_dst = []
input_dst = []
for o_val,i_val in zip(output_src,input_src):
    if not np.isnan(o_val):
        output_dst.append(o_val)
        input_dst.append(i_val)
    
with open(training_defn.train_input_filtered_fname,'wb') as f:
    pickle.dump(input_dst,f)
with open(training_defn.train_output_filtered_fname,'wb') as f:
    pickle.dump(output_dst,f)
