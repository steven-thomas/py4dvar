"""
framework: turns directory into a package
packages can be imported
eg: from <package> import <module>

any code in this file is run the first time this package is imported

imports listed here are for easier access to data classes
eg: "import datadef.UnknownData" instead of "import datadef.unknown_data.UnknownData"
"""

from fourdvar.datadef.unknown_data import UnknownData
from fourdvar.datadef.physical_data import PhysicalData
from fourdvar.datadef.model_input_data import ModelInputData
from fourdvar.datadef.model_output_data import ModelOutputData
from fourdvar.datadef.observation_data import ObservationData
from fourdvar.datadef.adjoint_forcing_data import AdjointForcingData
from fourdvar.datadef.sensitivity_data import SensitivityData
from fourdvar.datadef.physical_adjoint_data import PhysicalAdjointData
