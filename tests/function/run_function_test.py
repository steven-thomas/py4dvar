
import unittest

import _get_root
import fourdvar.datadef as d
import fourdvar.user_driver as ud
from fourdvar._main_driver import get_answer
from fourdvar._transform import transform
from tests.function.config_function_test import cfg

def example_check( testcase, do_set_tear, testcls ):
    ( do_test, setup, teardown ) = do_set_tear
    if do_test is not True:
        return None
    if setup is not None:
        setup()
    example_instance = testcls.example()
    testcase.assertIsInstance( example_instance, testcls )
    testcase.assertTrue( example_instance.has_require( True ) )
    if teardown is not None:
        teardown()
    return None

def transform_check( testcase, do_set_tear, incls, outcls ):
    func_check( testcase, do_set_tear, transform, [incls.example(), outcls], outcls )
    return None

def func_check( testcase, do_set_tear, func, args, outcls ):
    ( do_test, setup, teardown ) = do_set_tear
    if do_test is not True:
        return None
    if setup is not None:
        setup()
    outinst = func( *args )
    testcase.assertIsInstance( outinst, outcls )
    if teardown is not None:
        teardown()
    return None

class TestExample( unittest.TestCase ):
    def setup( self ):
        pass
    def teardown( self ):
        pass
    def test_unknown_example( self ):
        example_check( self, cfg['test_unknown_example'], d.UnknownData )
    def test_physical_example( self ):
        example_check( self, cfg['test_physical_example'], d.PhysicalData )
    def test_model_input_example( self ):
        example_check( self, cfg['test_model_input_example'], d.ModelInputData )
    def test_model_output_example( self ):
        example_check( self, cfg['test_model_output_example'], d.ModelOutputData )
    def test_observation_example( self ):
        example_check( self, cfg['test_observation_example'], d.ObservationData )
    def test_adjoint_forcing_example( self ):
        example_check( self, cfg['test_adjoint_forcing_example'], d.AdjointForcingData )
    def test_sensitivity_example( self ):
        example_check( self, cfg['test_sensitivity_example'], d.SensitivityData )

class TestObservation( unittest.TestCase ):
    def setup( self ):
        pass
    def teardown( self ):
        pass
    def test_observation_weight( self ):
        func = d.ObservationData.weight
        args = [ d.ObservationData.example() ]
        func_check( self, cfg['test_observation_weight'], func, args, d.ObservationData )
    def test_observation_residual( self ):
        func = d.ObservationData.get_residual
        args = [ d.ObservationData.example(), d.ObservationData.example() ]
        func_check( self, cfg['test_observation_weight'], func, args, d.ObservationData )

class TestTransform( unittest.TestCase ):
    def setup( self ):
        pass
    def teardown( self ):
        pass
    def test_condition_transform( self ):
        transform_check( self, cfg['test_condition_transform'], d.PhysicalData, d.UnknownData )
    def test_uncondition_transform( self ):
        transform_check( self, cfg['test_uncondition_transform'], d.UnknownData, d.PhysicalData )
    def test_prepare_model_transform( self ):
        transform_check( self, cfg['test_prepare_model_transform'], d.PhysicalData, d.ModelInputData )
    def test_run_model_transform( self ):
        transform_check( self, cfg['test_run_model_transform'], d.ModelInputData, d.ModelOutputData )
    def test_obs_operator_transform( self ):
        transform_check( self, cfg['test_obs_operator_transform'], d.ModelOutputData, d.ObservationData )
    def test_calc_forcing_transform( self ):
        transform_check( self, cfg['test_calc_forcing_transform'], d.ObservationData, d.AdjointForcingData )
    def test_run_adjoint_transform( self ):
        transform_check( self, cfg['test_run_adjoint_transform'], d.AdjointForcingData, d.SensitivityData )
    def test_condition_adjoint_transform( self ):
        transform_check( self, cfg['test_condition_adjoint_transform'], d.SensitivityData, d.UnknownData )

class TestDriver( unittest.TestCase ):
    def setup( self ):
        pass
    def teardown( self ):
        pass
    def test_setup_driver( self ):
        func_check( self, cfg['test_setup_driver'], ud.setup, [], None.__class__ )
    def test_teardown_driver( self ):
        func_check( self, cfg['test_teardown_driver'], ud.teardown, [], None.__class__ )
    def test_get_background_driver( self ):
        func_check( self, cfg['test_get_background_driver'], ud.get_background, [], d.PhysicalData )
    def test_get_observed_driver( self ):
        func_check( self, cfg['test_get_observed_driver'], ud.get_observed, [], d.ObservationData )
    def test_full_driver( self ):
        func_check( self, cfg['test_full_driver'], get_answer, [], None.__class__ )
        
if __name__ == '__main__':
    unittest.main()

