
from __future__ import absolute_import

import numpy as np

#-CONFIG-SETTINGS-

max_quality_only = True
surface_type = 0         # 0=land,  1=ocean, -1=both
operation_mode = 1       # 0=glint, 1=nadir, -1=both
group_by_second = True
group_by_column = True

error_ocean = 0.5
error_land = 0.8

#-----------------

def merge_second( sounding_list ):

    value = np.array( [ s['xco2'] for s in sounding_list ] )
    unc = np.array( [ s['xco2_uncertainty'] for s in sounding_list ] )
    
    def weight_avg( s_list, var ):
        var_arr = np.array( [ s[var] for s in s_list ] )
        weights = 1/(unc**2)
        if var_arr.ndim == 1:
            w_arr = var_arr * weights
            sum_w_var = np.sum( w_arr )
        else:
            w_arr = np.transpose(var_arr) * weights
            sum_w_var = np.sum( w_arr, axis=1 )
        return sum_w_var / np.sum(weights)

    #average of the xco2 uncertainty, assume errors are completely correlated
    snum = len( sounding_list )
    avg_var_unc = (np.sum(unc)**2)/snum
    avg_unc = unc.mean()
    xco2_w_avg = weight_avg( sounding_list, 'xco2' )
    spread_ret = np.sqrt( ((xco2_w_avg - value)**2).mean() )
    
    #use spread if it is higher than reported uncertainty
    surface_type = int( sounding_list[0]['surface_type'] )
    my_err = error_land if surface_type == 1 else error_ocean
    if spread_ret == 0.:
        avg_spread = my_err
    else:
        avg_spread = max( spread_ret, my_err/float(snum) )
    avg_unc = max( avg_unc, avg_spread )

    key_list = sounding_list[0].keys()
    out_dict = {}
    for k in key_list:
        if k == 'xco2_uncertainty':
            out_dict[k] = avg_unc
        elif k == 'surface_type':
            out_dict[k] = surface_type
        elif k == 'operation_mode':
            out_dict[k] = sounding_list[0]['operation_mode']
        else:
            out_dict[k] = weight_avg( sounding_list, k )

    return out_dict

def is_single_column( obs ):
    col_set = set([ (c[3],c[4],) for c in obs['weight_grid'].keys() ])
    return (len(col_set) == 1)

def get_col_id( obs ):
    surface = [ (v,c) for c,v in obs['weight_grid'].items() if c[2]==0 ]
    coord = max(surface)[1]
    coord_id = (coord[0], coord[1], coord[3], coord[4],)
    return coord_id

def merge_column( obs_list ):
    unc = [ o['uncertainty'] for o in obs_list ]
    value = [ o['value'] for o in obs_list ]
    offset = [ o['offset_term'] for o in obs_list ]
    weight = 1./(np.array(unc)**2)
    avg_unc = 1./np.sqrt(weight.sum())
    avg_value = (weight * np.array(value)).sum() / weight.sum()
    avg_offset = (weight * np.array(offset)).sum() / weight.sum()

    all_coord = set()
    for o in obs_list:
        all_coord = all_coord.union( set(o['weight_grid'].keys()) )

    avg_weight_grid = {}
    for coord in all_coord:
        c_unc = []
        c_val = []
        for o in obs_list:
            try:
                c_val.append( o['weight_grid'][coord] )
                c_unc.append( o['uncertainty'] )
            except KeyError:
                pass
        w_val = ( ( (1./np.array(c_unc)**2) * np.array(c_val) ).sum()
                  / (1./np.array(c_unc)**2).sum() )
        avg_weight_grid[coord] = w_val
    out_dict = { 'uncertainty': avg_unc,
                 'value': avg_value,
                 'offset_term': avg_offset,
                 'weight_grid': avg_weight_grid }
    return out_dict
