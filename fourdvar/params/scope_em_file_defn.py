
import os

from fourdvar.params.root_path_defn import store_path

em_path = os.path.join( store_path, 'emulate' )

#list of input structs & emulation files, for each model index.
em_input_struct_fname = [
    os.path.join( em_path, 'test_input.pic' )
]

emulation_fname = [
    os.path.join( em_path, 'test_emulate.npz' )
]

