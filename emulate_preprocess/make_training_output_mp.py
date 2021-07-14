
import os
import sys
import pickle
import uuid
import numpy as np
import multiprocessing as mp

import context
import emulate_preprocess.p4d_scope_func as scope
import emulate_preprocess.training_defn as training_defn
import fourdvar.params.scope_em_file_defn as em_file_defn

input_fname = em_file_defn.em_input_struct_fname
scope.set_input( input_fname )

def mp_scope_wrapper(x):
    dname = 'TMPDIR-' + str(uuid.uuid4())
    return scope.vector_scope([x], dname=dname)

try:
    nproc = int(sys.argv[1])
except:
    raise ValueError('Must provde number of processes.')

with open( training_defn.train_input_raw_fname, 'rb' ) as f:
    input_list = pickle.load(f)

with mp.Pool(processes=nproc) as pool:
    output_list = pool.map(mp_scope_wrapper, [x for x in input_list] )

with open( training_defn.train_output_raw_fname, 'wb' ) as f:
    pickle.dump( output_list, f )
