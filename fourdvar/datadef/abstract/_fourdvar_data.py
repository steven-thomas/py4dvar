# NOT FOR USER MODIFICATION
#this is the highest level abstract data class
#every data object will have this as a parent

import numpy as np

class FourDVarData( object ):
    """the abstarct global class for all FourDVar data structures"""
    require = set()
    
    def has_require( self, check_seq=False ):
        """tests that every attribute named in 'required' is defined and not None.
        This function is recursive on attributes subclassed from FourDVarData.
        """
        for name in self.require:
            if name not in self.__dict__.keys():
                return False
            elif self.__dict__[ name ] is None:
                return False
            elif isinstance( self.__dict__[ name ], FourDVarData ):
                if not self.__dict__[ name ].has_require( check_seq ):
                    return False
            elif check_seq and not self._check_seq( self.__dict__[ name ] ):
                return False
        return True
    
    def _check_seq( self, obj ):
        try:
            obj_iter = obj.items()
        except AttributeError:
            if isinstance( obj, str ):
                return True
            try:
                obj_iter = enumerate( obj )
            except TypeError:
                #not an iterable
                return True
        for i,v in obj_iter:
            if isinstance( v, FourDVarData ) and not v.has_require( True ):
                return False
            if not self._check_seq( v ):
                return False
        return True
    
    @classmethod
    def add_require( cls, *args ):
        """return a new require set that includes every string listed in args"""
        assert all([ type( x ) is str for x in args ]), 'require set must only contain strings'
        return cls.require.union( args )

