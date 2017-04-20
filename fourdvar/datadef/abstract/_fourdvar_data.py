"""
framework: top-level abstraction for a data class
any method added here will be available to all data classes
"""

import numpy as np

class FourDVarData( object ):
    """framework: the abstarct global class for all FourDVar data structures"""
    
    def cleanup( self ):
        """
        framework: generic cleanup function
        input: None
        output: None
        
        notes: currently only a stub, allows no-op cleanup.
        """
        pass
        return None

