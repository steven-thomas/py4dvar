#make directory into package
#run any loading/setup required by whole package

import _get_root
from fourdvar.transfunc.calc_forcing import calc_forcing
from fourdvar.transfunc.condition import condition
from fourdvar.transfunc.condition_adjoint import condition_adjoint
from fourdvar.transfunc.obs_operator import obs_operator
from fourdvar.transfunc.prepare_model import prepare_model
from fourdvar.transfunc.run_adjoint import run_adjoint
from fourdvar.transfunc.run_model import run_model
from fourdvar.transfunc.uncondition import uncondition

