import config # should come from parent
from utility.general import classFromModule
import baseSector
import importlib
# now extract the sector classes we need, taken from the config{'sectors'} variable
classList = [classFromModule(name, baseclass=baseSector.BaseSector, postfix='Sector', anchor='sector') for name in config.config['sectors']]
