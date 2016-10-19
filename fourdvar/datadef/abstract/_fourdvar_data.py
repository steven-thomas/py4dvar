"""
framework: top-level abstraction for a data class
any method added here will be available to all data classes
"""

import numpy as np

class FourDVarData( object ):
    """framework: the abstarct global class for all FourDVar data structures"""
    
    #the set of attributes a data structure must have defined in order to be valid
    require = set()
    
    def has_require( self, check_seq=False ):
        """
        framework: does a data structure have all 'require' attributes defined.
        input: Boolean (should lists of data structures be tested as well)
        output: Boolean (are requirements met)
        
        eg: is_ready = model_input.has_require( False )
        
        notes: this function is recursive.
        If an attribute tested is another data structure it must pass as well.
        check_seq=True means that is a list of data structures is tested every element must pass as well.
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
        """
        framework: run has_require() on every element of a sequence
        *note* this function should only be called internally.
        """
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
        """
        framework: return a new require set that includes every string listed in args and previous requirements
        input: strings (arbitrary number of)
        output: set (assign to require)
        
        eg: (PhysicalData example)
        class PhysicalData( InterfaceData ):
            require = InterfaceData.add_require( 'row_count', 'col_count', 'lay_count', ... )
        """
        assert all([ type( x ) is str for x in args ]), 'require set must only contain strings'
        return cls.require.union( args )
    
    def cleanup( self ):
        """
        framework: generic cleanup function
        input: None
        output: None
        
        notes: currently only a stub, used to allow no-op cleanup.
        """
        pass
        return None

