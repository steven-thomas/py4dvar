"""
no_transport_finite_diff_test.py

Copyright 2016 University of Melbourne.
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""
# Run a simple no transport dot-test to check adjoint math.
# This test is only valid for 1-hour resolution output & sensitivities.

import numpy as np
import os

import context
import fourdvar.datadef as d
from fourdvar._transform import transform
import fourdvar.user_driver as user
import fourdvar.params.template_defn as template
import fourdvar.params.cmaq_config as cmaq
import fourdvar.util.date_handle as dt
import fourdvar.util.netcdf_handle as ncf
import fourdvar.params.archive_defn as archive_defn
import fourdvar.util.archive_handle as archive

spcs_list = ['CO2'] # species to perturb within CMAQ.
tsec = 3600. #seconds per timestep, DO NOT MODIFY

archive_defn.experiment = 'tmp_finite_diff_test'
archive_defn.desc_name = ''
archive_path = archive.get_archive_path()

def make_perturbation( init_vector, scale ):
    """Increase block of values by uncertainty*scale at:
     - The first time-step of PhysicalData
     - Only on the surface layer
     - In the middle of the domain
     - For every species
    """
    unknown = d.UnknownData( init_vector )
    p = transform( unknown, d.PhysicalData )
    #edit physical (p)
    r, c = int(p.nrows/3), int(p.ncols/3)
    for spc in p.spcs:
        p.emis[spc][0,0,r:2*r,c:2*c] += scale*p.emis_unc[spc][0,0,r:2*r,c:2*c]
    #convert perturbed phys back into vector
    pert_unknown = transform( p, d.UnknownData )
    return pert_unknown.get_vector()

def make_forcing():
    """put a block of forcing at:
     - The second last time-step of the last day
     - Only on the surface layer
     - In the middle of the domain
     - For every species
    """
    nstep,nlay,nrow,ncol = ncf.get_variable( template.force, spcs_list[0] ).shape

    for date in dt.get_datelist():
        force = { spc: np.zeros((nstep,nlay,nrow,ncol,)) for spc in spcs_list }
        if date == dt.get_datelist()[-1]:
            for arr in force.values():
                trow, tcol = int(nrow/3), int(ncol/3)
                arr[ -2, 0, trow:2*trow, tcol:2*tcol ] = 1.
        f_file = dt.replace_date( cmaq.force_file, date )
        ncf.create_from_template( template.force, f_file, var_change=force,
                                  date=date, overwrite=True )
    return d.AdjointForcingData()

def fwd_no_transport( model_input ):
    """mimic CMAQ_fwd with no transport.
    assumes ALL files have a 1-hour timestep"""
    #get nlays conc
    c_lay = ncf.get_variable( template.conc, spcs_list[0] ).shape[1]
    #get nlays emis
    e_lay = ncf.get_variable( dt.replace_date( template.emis, dt.start_date ),
                              spcs_list[0] ).shape[1]
    #get icon for each species
    icon = ncf.get_variable( cmaq.icon_file, spcs_list )
    #get constants to convert emission units
    mwair = 28.9628
    ppm_scale = 1E6
    kg_scale = 1E-3
    srcfile = dt.replace_date( cmaq.met_cro_3d, dt.start_date )
    xcell = ncf.get_attr( srcfile, 'XCELL' )
    ycell = ncf.get_attr( srcfile, 'YCELL' )
    lay_sigma = list( ncf.get_attr( srcfile, 'VGLVLS' ) )
    lay_thick = [ lay_sigma[i]-lay_sigma[i+1] for i in range( e_lay ) ]
    lay_thick = np.array(lay_thick).reshape(( 1, e_lay, 1, 1 ))
    emis_scale = (ppm_scale*kg_scale*mwair) / (lay_thick*xcell*ycell) # * RRHOJ
    #run fwd
    for date in dt.get_datelist():
        conc = ncf.get_variable( template.conc, spcs_list )
        emis = ncf.get_variable( dt.replace_date(cmaq.emis_file,date), spcs_list )
        rhoj = ncf.get_variable( dt.replace_date(cmaq.met_cro_3d,date), "DENSA_J" )
        for spc,c_arr in conc.items():
            c_arr[:,:,:,:] = icon[spc][:,:c_lay,:,:]
            e_arr = emis_scale * emis[spc][:-1,...]
            e_arr = 2*tsec*e_arr / (rhoj[:-1,:e_lay,:,:] + rhoj[1:,:e_lay,:,:])
            c_arr[1:,:e_lay,:,:] += np.cumsum( e_arr, axis=0 )
            #update icon for next day
            icon[spc] = c_arr[-1:,...]
        #write conc file
        c_file = dt.replace_date( cmaq.conc_file, date )
        ncf.create_from_template( template.conc, c_file, var_change=conc,
                                  date=date, overwrite=True )
    return d.ModelOutputData()

def bwd_no_transport( adjoint_forcing ):
    """mimic CMAQ_bwd with no transport.
    assumes ALL files have a 1-hour timestep"""
    #get nlays for force, sense & sense_emis
    f_lay = ncf.get_variable( template.force, spcs_list[0] ).shape[1]
    s_lay = ncf.get_variable( template.sense_conc, spcs_list[0] ).shape[1]
    e_lay = ncf.get_variable( template.sense_emis, spcs_list[0] ).shape[1]

    #get icon for each species, init as 0.
    nstep,_,row,col = ncf.get_variable( template.force, spcs_list[0] ).shape
    icon = { spc:np.zeros((s_lay,row,col,)) for spc in spcs_list }

    for date in dt.get_datelist()[::-1]:
        force = ncf.get_variable( dt.replace_date(cmaq.force_file,date), spcs_list )
        conc = {}
        emis = {}
        for spc in spcs_list:
            bwd_arr = np.zeros((nstep,s_lay,row,col))
            bwd_arr[-1,:,:,:] = icon[spc][:,:,:]
            bwd_arr[:-1,:,:,:] = force[spc][1:,:s_lay,:,:]
            s_arr = np.cumsum( bwd_arr[::-1,:,:,:], axis=0 )[::-1,:,:,:]
            icon[spc][:] = s_arr[0,:,:,:].copy()
            conc[spc] = s_arr[:,:s_lay,:,:].copy()
            emis[spc] = s_arr[:,:e_lay,:,:].copy() * float(tsec)
        #write sensitivity files
        c_file = dt.replace_date( cmaq.conc_sense_file, date )
        e_file = dt.replace_date( cmaq.emis_sense_file, date )
        ncf.create_from_template( template.sense_conc, c_file, var_change=conc,
                                  date=date, overwrite=True )
        ncf.create_from_template( template.sense_emis, e_file, var_change=emis,
                                  date=date, overwrite=True )
    return d.SensitivityData()

def partial_adjoint( vector ):
    unknown = d.UnknownData( vector )
    physical = transform( unknown, d.PhysicalData )
    model_input = transform( physical, d.ModelInputData )
    model_output = fwd_no_transport( model_input )
    adjoint_forcing = make_forcing()
    sensitivity = bwd_no_transport( adjoint_forcing )
    phys_adjoint = transform( sensitivity, d.PhysicalAdjointData )
    unk_adjoint = transform( phys_adjoint, d.UnknownData )
    vec_adjoint = unk_adjoint.get_vector()
    return vec_adjoint

def finite_diff( scale ):
    prior_phys = user.get_background()
    unknowns = transform( prior_phys, d.UnknownData )
    init_vector = unknowns.get_vector()

    init_gradient = partial_adjoint( init_vector )
    d.ModelOutputData().archive( 'init_conc' )

    pert_vector = make_perturbation( init_vector, scale )
    pert_gradient = partial_adjoint( pert_vector )
    d.ModelOutputData().archive( 'pert_conc' )
    d.AdjointForcingData().archive( 'force' )

    eps = 1e-6
    if abs(pert_gradient-init_gradient).sum() > eps*abs(pert_gradient).sum():
        print "WARNING: pert & init gradients differ."
        print "init gradient norm = {:}".format( np.linalg.norm(init_gradient) )
        print "pert gradient norm = {:}".format( np.linalg.norm(pert_gradient) )

    pert_diff = pert_vector - init_vector
    sense_score = .5*( (pert_diff*init_gradient).sum() + (pert_diff*pert_gradient).sum() )

    force_score = 0.
    iconc_file = os.path.join( archive_path, 'init_conc', archive_defn.conc_file )
    pconc_file = os.path.join( archive_path, 'pert_conc', archive_defn.conc_file )
    force_file = os.path.join( archive_path, 'force', archive_defn.force_file )
    for date in dt.get_datelist():
        iconc = ncf.get_variable( dt.replace_date(iconc_file,date), spcs_list )
        pconc = ncf.get_variable( dt.replace_date(pconc_file,date), spcs_list )
        force = ncf.get_variable( dt.replace_date(force_file,date), spcs_list )
        c_diff = { s: pconc[s] - iconc[s] for s in spcs_list }
        force_score += sum([ (c_diff[s] * force[s]).sum() for s in spcs_list ])
    
    return sense_score, force_score

if __name__ == "__main__":
    #perturbation = scale * uncertainty.
    sense, force = finite_diff( scale=1. )
    print 40*'-'
    print 'sensitivity dot perturbation = {:}'.format( sense )
    print 'forcing dot conc_change = {:}'.format( force )
    print 'abs difference = {:}'.format( abs( sense-force ) )
    print 'rel difference = {:}'.format( 2.*abs(sense-force) / (sense+force) )
    print 40*'-'
