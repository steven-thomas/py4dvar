"""
emulate_input_struct.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np
import pickle

class EmulationInput( object ):

    var_param = []

    def add_var( self, name, min_val, max_val, shape, is_target ):
        var_dict = {}
        var_dict['name'] = name
        var_dict['shape'] = shape
        if shape == None:
            var_dict['size'] = 1
            var_dict['min_val'] = float( min_val )
            var_dict['max_val'] = float( max_val )
        else:
            var_dict['size'] = np.prod(shape)
            var_dict['min_val'] = np.array( min_val )
            var_dict['max_val'] = np.array( max_val )
            assert var_dict['min_val'].shape == shape
            assert var_dict['max_val'].shape == shape
        var_dict['is_target'] = bool( is_target )
        self.var_param.append( var_dict )
        return None

    def get_list( self, key ):
        src_list = [ v[key] for v in self.var_param ]
        size_list = [ v['size'] for v in self.var_param ]
        val_list = []
        for val,size in zip( src_list, size_list ):
            if size == 1:
                val_list.append(val)
            elif type(val) == np.ndarray:
                val_list.extend( list(val.flatten()) )
            else:
                val_list.extend( size * [val] )
        return val_list

    def save( self, fname ):
        with open( fname, 'wb' ) as f:
            pickle.dump( self.var_param, f )
        return None

    @classmethod
    def load( cls, fname ):
        x = cls()
        with open(fname, 'rb') as f:
            x.var_param = pickle.load( f )
        return x
