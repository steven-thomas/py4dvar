#make directory into package
#run any loading/setup required by whole package

#run import of non-abstract classes for external access / simpler naming

import _get_root
from fourdvar.datadef.unknown_data import UnknownData
from fourdvar.datadef.physical_data import PhysicalData
from fourdvar.datadef.model_input_data import ModelInputData
from fourdvar.datadef.model_output_data import ModelOutputData
from fourdvar.datadef.observation_data import ObservationData
from fourdvar.datadef.adjoint_forcing_data import AdjointForcingData
from fourdvar.datadef.sensitivity_data import SensitivityData

