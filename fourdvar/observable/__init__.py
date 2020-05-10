import config
from utility.general import classFromModule
import baseObservable
import importlib
# now extract the observable classes we need, taken from the config{'observables'} variable
classList = [classFromModule(name, baseclass=baseObservable.BaseObservable, postfix='Observable', anchor='observable') for name in config.config['observables']]
