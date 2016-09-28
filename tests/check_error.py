#run tests from the 'function' package to check that required components do not generate errors

import _get_root
from tests._function_test import check_functions

#User parameters
###########################################################################################

# The list of all the python interpreters to test with
python_interp = [ '/bin/python2', '/bin/python3' ]
#python_interp = [ 'python' ]

# The list of tests to run. Must be in tests/function package. Use 'all' to run every test 
#test_list = ['test_all_datadef_example.py', 'test_cost_func.py', 'test_grad_func.py']
test_list = 'all'

# file to save the summary to (if applicable)
summary_filename = 'summary.log'

# Where to display the pass/fail results for each test.
# Must be one of: 'screen' (print to screen), 'file' (save to file), or 'none' (ignore summary)
summary_output = 'screen'

# file to save the error traceback to (if applicable)
traceback_filename = 'error_output.log'

# Where to display the traceback of all failed tests.
# Must be one of: 'screen' (print to screen), 'file' (save to file), or 'none' (ignore traceback)
traceback_output = 'file'

###########################################################################################

check_functions( python_interp, test_list,
                summary_filename, summary_output,
                traceback_filename, traceback_output )

