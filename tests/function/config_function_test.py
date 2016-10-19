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
from fourdvar.util.file_handle import rmall
from fourdvar.datadef import ModelOutputData

#function, not output
get_traj = ModelOutputData.example

cfg = {
    'test_unknown_example':                 [ True,     None,       None ],
    'test_physical_example':                [ True,     None,       None ],
    'test_model_input_example':             [ True,     None,       None ],
    'test_model_output_example':            [ True,     None,       None ],
    'test_observation_example':             [ True,     None,       None ],
    'test_adjoint_forcing_example':         [ True,     None,       None ],
    'test_sensitivity_example':             [ True,     None,       None ],
    'test_observation_weight':              [ True,     None,       None ],
    'test_observation_residual':            [ True,     None,       None ],
    'test_condition_transform':             [ True,     None,       None ],
    'test_uncondition_transform':           [ True,     None,       None ],
    'test_prepare_model_transform':         [ True,     None,       None ],
    'test_run_model_transform':             [ True,     None,       None ],
    'test_obs_operator_transform':          [ True,     None,       None ],
    'test_calc_forcing_transform':          [ True,     get_traj,   rmall ],
    'test_run_adjoint_transform':           [ True,     get_traj,   rmall ],
    'test_condition_adjoint_transform':     [ True,     None,       None ],
    'test_setup_driver':                    [ True,     None,       None ],
    'test_cleanup_driver':                  [ True,     None,       None ],
    'test_get_background_driver':           [ True,     None,       None ],
    'test_get_observed_driver':             [ True,     None,       None ],
    'test_full_driver':                     [ True,     None,       None ]
}

