"""
prepare_model.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

import numpy as np

from fourdvar.datadef import PhysicalData, ModelInputData
import fourdvar.util.date_handle as dt
import fourdvar.params.template_defn as template
import fourdvar.util.netcdf_handle as ncf
import fourdvar.util.cmaq_handle as cmaq
from fourdvar.params.input_defn import inc_icon

#value to convert units for each days emissions
unit_convert = None

def get_unit_convert():
    """
    extension: get unit conversion value
    input: None
    output: scalar
    
    notes: PhysicalData.emis units = mol/(s*m^2)
           ModelInputData.emis units = mol/s
    """
    fname = dt.replace_date( template.emis, dt.start_date )
    xcell = ncf.get_attr( fname, 'XCELL' )
    ycell = ncf.get_attr( fname, 'YCELL' )
    return  float(xcell*ycell)

def prepare_model( physical_data ):
    """
    application: change resolution/formatting of physical data for input in forward model
    input: PhysicalData
    output: ModelInputData
    """
    global unit_convert
    if unit_convert is None:
        unit_convert = get_unit_convert()

    if inc_icon is True:
        model_input_args = { 'icon': {} }
        #physical icon has no time dim, model input icon has time dim of len 1
        for spcs, icon_array in physical_data.icon.items():
            model_input_args['icon'][spcs] = icon_array.reshape( (1,)+icon_array.shape )
    else:
        model_input_args = {}
    
    diurnal = ncf.get_variable( template.diurnal, physical_data.spcs )
        
    emis_pattern = 'emis.<YYYYMMDD>'
    for i,date in enumerate( dt.get_datelist() ):
        spcs_dict = {}
        pstep = int( i // physical_data.tday )
        for spcs_name in physical_data.spcs:
            model_arr = np.zeros( diurnal[ spcs_name ].shape )
            for c,_ in enumerate( physical_data.cat ):
                phys_arr = physical_data.emis[ spcs_name ][ c, pstep, ... ]
                phys_arr[ np.isnan( phys_arr ) ] = 0.
                model_arr += phys_arr * (diurnal[ spcs_name ] == c)
            spcs_dict[ spcs_name ] = model_arr * unit_convert
        emis_argname = dt.replace_date( emis_pattern, date )
        model_input_args[ emis_argname ] = spcs_dict
    
    #may want to remove this line in future.
    cmaq.wipeout_fwd()
    
    return ModelInputData.create_new( **model_input_args )
