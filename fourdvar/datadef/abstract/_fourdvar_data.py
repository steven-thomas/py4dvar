# NOT FOR USER MODIFICATION
#this is the highest level abstract data class
#every data object will have this as a parent

import numpy as np

class FourDVarData( object ):
    """the abstarct global class for all FourDVar data structures"""
    
    def __init__( self ):
        self.required = set()
        return None
    
    def has_requirements( self ):
        """tests that every attribute named in 'required' is defined and not None.
        This function is recursive on attributes subclassed from FourDVarData.
        """
        
        for name in self.required:
            if name not in self.__dict__.keys():
                return False
            elif self.__dict__[ name ] is None:
                return False
            elif isinstance( self.__dict__[ name ], FourDVarData ):
                if not self.__dict__[ name ].has_requirements():
                    return False
        return True

