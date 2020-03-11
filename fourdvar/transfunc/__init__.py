"""
framework: turns directory into a package
packages can be imported
eg: from <package> import <module>

any code in this file is run the first time this package is imported

imports listed are for easier naming and importing

eg: "import transfunc.run_model" instead of "import transfunc.run_model.run_model"
"""

from fourdvar.transfunc.calc_forcing import calc_forcing
from fourdvar.transfunc.condition import condition
from fourdvar.transfunc.condition import condition_adjoint
from fourdvar.transfunc.map_sense import map_sense
from fourdvar.transfunc.obs_operator import obs_operator
from fourdvar.transfunc.prepare_model import prepare_model
from fourdvar.transfunc.run_adjoint import run_adjoint
from fourdvar.transfunc.run_model import run_model
from fourdvar.transfunc.uncondition import uncondition
