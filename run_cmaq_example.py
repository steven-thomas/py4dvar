
import _get_root
import fourdvar.datadef as d
from fourdvar._transform import transform
import fourdvar.util.cmaq_handle as cmaq

m_in = d.ModelInputData.example()
m_in.archive()
m_out = transform( m_in, d.ModelOutputData )
m_out.archive()

frc = d.AdjointForcingData.example()
frc.archive()
sense = transform( frc, d.SensitivityData )
sense.archive()

cmaq.cleanup()
