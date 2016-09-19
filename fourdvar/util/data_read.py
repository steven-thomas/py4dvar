# the get_dict function reads a csv-formatted file saved in the projects data directory
# (fourdvar/data) and returns a dictionary with keys from the first line and value lists
# from each column matching its key.
# Values after the keys are converted into floats.

import os

data_loc = os.path.join( os.path.realpath( os.path.join( os.path.dirname( __file__ ), '..' ) ), 'data' )

def get_dict( f_name ):
    file_obj = open( os.path.join( data_loc, f_name ), 'r' )
    lines = file_obj.readlines()
    file_obj.close()
    
    items = []
    for l in lines:
        if (l.strip() != ''):
            sliced = l.split( ',' )
            items.append( [ s.strip() for s in sliced ] )
    
    out_dict = {}
    key_str = items.pop( 0 )
    for n in range( len( key_str ) ):
        out_dict[ key_str[ n ] ] = [ float(i[n]) for i in items ]
    
    return out_dict

