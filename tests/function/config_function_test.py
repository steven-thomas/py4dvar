"""
application: config settings for function tests
each test named has 3 setting: [run, setup, teardown]

run:      Boolean  - If False test is not run but listed as having passed anyway.
setup:    function - Must take no arguments, is called before test is run.
                     Use to ensure required resources are available.
teardown: function - Must take no arguments, is called after test is run.
                     Use to cleanup unwanted output of test.
"""

import _get_root
#from fourdvar.util.file_handle import rmall
#from fourdvar.datadef import ModelOutputData

#function, not output
#get_traj = ModelOutputData.example

cfg = {
    'test_unknown_example':                 [ False,    None,       None ],
    'test_physical_example':                [ False,    None,       None ],
    'test_model_input_example':             [ True,     None,       None ],
    'test_model_output_example':            [ False,    None,       None ],
    'test_observation_example':             [ False,    None,       None ],
    'test_adjoint_forcing_example':         [ True,     None,       None ],
    'test_sensitivity_example':             [ False,    None,       None ],
    'test_observation_weight':              [ False,    None,       None ],
    'test_observation_residual':            [ False,    None,       None ],
    'test_condition_transform':             [ False,    None,       None ],
    'test_uncondition_transform':           [ False,    None,       None ],
    'test_prepare_model_transform':         [ False,    None,       None ],
    'test_run_model_transform':             [ False,    None,       None ],
    'test_obs_operator_transform':          [ False,    None,       None ],
    'test_calc_forcing_transform':          [ False,    None,       None ],
    'test_run_adjoint_transform':           [ False,    None,       None ],
    'test_condition_adjoint_transform':     [ False,    None,       None ],
    'test_setup_driver':                    [ False,    None,       None ],
    'test_cleanup_driver':                  [ False,    None,       None ],
    'test_get_background_driver':           [ False,    None,       None ],
    'test_get_observed_driver':             [ False,    None,       None ],
    'test_full_driver':                     [ False,    None,       None ]
}

