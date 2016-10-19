"""
framework: abstract class for data structures that store data in arbitrary formats
"""

import numpy as np

import _get_root
from fourdvar.datadef.abstract._fourdvar_data import FourDVarData

class InterfaceData( FourDVarData ):
    """
    framework: abstract class for data stuctures passing between transform calls.
    """
    
    def cleanup( self ):
        """
        framework: concrete application must overwrite the cleanup method
        input: None
        output: <N/A> (raises error)
        """
        raise NotImplementedError( '{} requires cleanup method'.format( self.__class__.__name__ ) )

