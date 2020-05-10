import importlib
import re
def classFromModule( name, postfix=None, baseclass=None, anchor=None):
    """ returns a class imported from a module using the naming scheme described in ../README.org.
    The class and module names are formed by adding the optional postfix. 
    If baseclass is not None, check if the class is a subclass of baseclass.
    anchor the import at the package named by anchor.
    to handle modules in subpackages use the anchor not the module name"""
    titlename = name.lower().title()
    lowername = name.lower()
    if postfix is not None:
        modulename = lowername +postfix
    else:
        modulename = lowername
    modulename = '.'+modulename # insist on relative import to anchor
    if postfix is not None:
        classname = titlename + postfix
    else:
        classname = titlename
    module = importlib.import_module( modulename, anchor)
    foundobj = getattr( module, classname)
    if baseclass is not None:
        if not issubclass( foundobj, baseclass): raise ValueError("{} not subclass of {}".format( classname, baseclass.__name_))
    return foundobj
