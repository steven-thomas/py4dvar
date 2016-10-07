# the get_dict function reads a csv-formatted file saved in the projects data directory
# (fourdvar/data) and returns a dictionary with keys from the first line and value lists
# from each column matching its key.
# Values after the keys are converted into floats.

import os
import numpy as np

data_loc = os.path.join( os.path.realpath( os.path.join( os.path.dirname( __file__ ), '..' ) ), 'data' )
fdict = {}

def get_dict( fname ):
    file_obj = open( os.path.join( data_loc, fname ), 'r' )
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

def save_array( label, data, fname, make_label_str=False ):
    global fdict
    assert type( data ) == np.ndarray, 'can only save a numpy array'
    if type( label ) != str:
        if make_label_str is True:
            label = label.__class__.__name__
        else:
            raise TypeError( 'invalid label for save_array: must be string or have make_label_str == True' )
    if label not in fdict.keys():
        fdict[ label ] = [ fname ]
    else:
        if fname in fdict[ label ]:
            fdict[ label ].remove( fname )
        fdict[ label ].insert( 0, fname )
    assert sum( l.count( fname ) for l in fdict.values() ) == 1, 'Only store 1 copy of every filename!'
    fpath = os.path.join( data_loc, fname )
    np.savetxt( fpath, data )
    return None

def load_array( label=None, fname=None, make_label_str=False ):
    assert ( label is None ) ^ ( fname is None ), 'Must provide either label or fname (but not both)'
    if label is not None:
        if make_label_str is True and type( label ) is not str:
            label = label.__class__.__name__
        assert label in fdict.keys(), 'unable to find label {}'.format( label )
        fname = fdict[ label ][ 0 ]
    fpath = os.path.join( data_loc, fname )
    data = np.loadtxt( fpath )
    return data

def rm( fname, fail_not_found=True ):
    global fdict
    fcount = sum( l.count( fname ) for l in fdict.values() )
    assert fcount <= 1, 'Only store 1 copy of every filename!'
    if fcount == 0:
        if fail_not_found is True:
            raise ValueError( 'unable to find {} to remove'.format( fname ) )
        return None
    for label, flist in list( fdict.items() ):
        if fname in flist:
            fdict[ label ].remove( fname )
            if len( fdict[ label ] ) == 0:
                fdict.pop( label )
    os.remove( os.path.join( data_loc, fname ) )
    return None

def rmall():
    for flist in list( fdict.values() ):
        for fname in flist:
            rm( fname )

