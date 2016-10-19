#run repeated test of minimizer and check variance.
import numpy as np

import _get_root
import fourdvar.datadef as d
import fourdvar._main_driver as main
import fourdvar.user_driver as user
from fourdvar._transform import transform

repeat = 100

true_phys = d.PhysicalData.example()
true_unk = transform( true_phys, d.UnknownData )
true_modin = transform( true_phys, d.ModelInputData )
true_modout = transform( true_modin, d.ModelOutputData )
true_obs = transform( true_modout, d.ObservationData )

true_modin.cleanup()
true_modout.cleanup()

for r in range( repeat ):
    prior = d.UnknownData.clone( true_unk )
    prior.perturb()
    main.bg_unknown = prior
    obs = d.ObservationData.clone( true_obs )
    obs.perturb()
    main.observed = obs
    user.setup()
    output = user.minim( main.cost_func, main.gradient_func, np.array( prior.get_vector( 'value' ) ) )
    user.cleanup()
    
    #from here on user informs how to handle output
    posterior = d.UnknownData( output[0] )
    out_phys = transform( posterior, d.PhysicalData )
    #out_phys.clone()/.save()/.remember()
    

