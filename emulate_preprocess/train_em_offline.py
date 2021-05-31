
import pickle
import numpy as np
import gp_emulator

import context
import emulate_preprocess.training_defn as training_defn
import fourdvar.params.scope_em_file_defn as em_file_defn

em_index = training_defn.em_training_index
em_fname = em_file_defn.emulation_fname_list[em_index]

with open(training_defn.train_input_filtered_fname, 'rb') as f:
    input_arr = np.array( pickle.load(f) )
with open(training_defn.train_output_filtered_fname, 'rb') as f:
    output_arr = np.array( pickle.load(f) )

gp = gp_emulator.GaussianProcess(inputs=input_arr, targets=output_arr)
gp.learn_hyperparameters()

gp.save_emulator( em_fname )
