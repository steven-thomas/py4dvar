"""
extension: all the file IO functions needed for the program
in this example all files are saved to and read from the fourdvar/data directory
"""

import os
import numpy as np

array_suffix = '.array'
#data directories full pathname
data_loc = os.path.join( os.path.realpath( os.path.join( os.path.dirname( __file__ ), '..' ) ), 'data' )
#tracking for all files created during a programs run
fdict = {}

def get_dict( fname ):
    """
    extension: read a csv-format file and return contents as a dictionary of lists
    input: string (filename)
    output: dictionary
    
    notes: first line of file are keys for dictionary. values are list from every following line
    all values are converted into floats. Will raise an error if not applicable
    """
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

def create_array( datacls, data ):
    """
    extension: save a numpy array to a file, remember this file in fdict, datacls name is used as key.
    input: class of data container (eg: ModelOutputData), numpy.ndarray
    output: string (filename)
    """
    assert isinstance( data, np.ndarray ), 'can only save a numpy array'
    
    label = datacls.__name__
    if label not in fdict.keys():
        fdict[ label ] = []
    
    make_name = lambda i: label + str(i) + array_suffix
    make_path = lambda i: os.path.join( data_loc, make_name(i) )
    i=0
    while os.path.isfile( make_path( i ) ):
        i += 1
    fname = make_name( i )
    fpath = make_path( i )
    
    fdict[ label ].insert( 0, fname )
    np.savetxt( fpath, data )
    return fname

def update_array( fname, data ):
    """
    extension: overwrite an existing saved array with new data
    input: string (filename), numpy.ndarray
    output: None
    """
    fpath = os.path.join( data_loc, fname)
    assert isinstance( data, np.ndarray ), 'can only save a numpy array'
    assert os.path.isfile( fpath ), 'file {} does not exist'.format( fname )
    assert sum( ls.count( fname ) for ls in fdict.values() ) == 1, 'must have 1 copy of {} in records'.format(fname)
    
    for label, ls in fdict.items():
        if fname in ls: break
    fdict[ label ].remove( fname )
    fdict[ label ].insert( 0, fname )
    np.savetxt( fpath, data )
    return None

def read_array( datacls=None, fname=None ):
    """
    extension: return numpy array either from filename or last updated class
    input: class of data container (eg: ModelOutputData), string (filename)
    output: numpy.ndarray
    
    notes: only need to provide one of filename for data class. If both provided filename is used.
    """
    #assert ( label is None ) ^ ( fname is None ), 'Must provide either label or fname (but not both)'
    if fname is None:
        assert datacls is not None, 'Must provide either label or fname'
        fname = fdict[ datacls.__name__ ][0]
    fpath = os.path.join( data_loc, fname )
    assert os.path.isfile( fpath ), 'file {} does not exist'.format( fname )
    data = np.loadtxt( fpath )
    return data

def rm( fname, fail_not_found=True ):
    """
    extension: delete a file and remove its tracking
    input: string (filename), Boolean (if file not found raise Error)
    output: None
    """
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
    """
    extension: delete every file tracked in fdict
    input: None
    output: None
    """
    for flist in list( fdict.values() ):
        for fname in flist:
            rm( fname )

