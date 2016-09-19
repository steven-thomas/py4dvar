# NOT FOR USER MODIFICATION
# interface data is the abstract class for 'default' data types
# any information that doesn't have specific access requirements is an interface class

import numpy as np

import _get_root
from fourdvar.datadef.abstract._fourdvar_data import FourDVarData

class InterfaceData( FourDVarData ):
    """This is the abstract class for data stuctures used only for passing between transform calls.
    This has less strict requirements for consistent layout, but less standard accessor methods
    """
    
    def __init__( self ):
        FourDVarData.__init__( self )
        return None

