"""
extension: all the file IO functions needed for the program
in this example all files are saved to and read from the fourdvar/data directory
"""

import os
import numpy as np

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

def save_array( label, data, fname, make_label_str=False ):
    """
    extension: save a numpy array to a file, remember this file in fdict
    input: label=class or string, data=numpy array, fname=string (filename), make_label_str=Boolean
    output: None
    
    notes: if make_label_str is True get label from from the name of the class of label input
    label is used as key when saving to fdict. value is list of filenames, most recently made first
    """
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
    """
    extension: load a numpy array from a file
    input: label=class or string, fname=string (filename), make_label_str=Boolean
    output: numpy.ndarray
    
    notes: if make_label_str is True get label text from the name of class of label input
    if label is provided use first element of fdict[ label ] as fname
    """
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

