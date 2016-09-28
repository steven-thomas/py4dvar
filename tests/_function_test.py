#run function test

import sys
import os
import subprocess

def check_functions( python_interp, test_list,
                summary_filename, summary_output,
                traceback_filename, traceback_output ):
    if not is_interp_valid( python_interp ): sys.exit(1)
    valid_tests = make_valid_test( test_list )
    if valid_tests is None: sys.exit(1)
    if not is_output_valid( summary_filename, summary_output ): sys.exit(1)
    if not is_output_valid( traceback_filename, traceback_output ): sys.exit(1)
    
    total = 0
    passed = 0
    summary_text = ''
    traceback_text = ''
    for py in python_interp:
        for test in valid_tests:
            total += 1
            status = 'unknown'
            returncode, errtxt = runtest( py, test )
            if returncode == 0:
                passed += 1
                status = 'passed'
            else:
                status = 'failed'
                traceback_text += '{}\n{}\n\n'.format( py, errtxt )
            testname = os.path.basename( test )
            pyname = os.path.basename( py )
            summary_text += '{} {} with {}\n'.format( status, testname, pyname )

    if total == passed:
        summary_text += 'All {} tests passed!\n'.format( passed )
    else:
        summary_text += 'Failed {} out of {}.\n'.format( total - passed, total )
    
    display( traceback_text, traceback_filename, traceback_output )
    display( summary_text, summary_filename, summary_output )
    return None

def runtest( py, test ):
    proc = subprocess.Popen([ py, test ], stdout=subprocess.PIPE, stderr=subprocess.PIPE )
    outtxt, errtxt = proc.communicate()
    returncode = proc.returncode
    return returncode, errtxt

def is_interp_valid( python_interp ):
    #check all provided interpreters work
    isvalid = True
    null_out = open( os.devnull, 'w' )
    for py in python_interp:
        try:
            subprocess.call([ py, '/' ], stderr=null_out)
        except OSError:
            print( 'cannot recognize {}'.format( py ) )
            isvalid = False
    null_out.close()
    return isvalid

def make_valid_test( test_list ):
    #check all provided tests exist inside test_dir
    loc = os.path.dirname( os.path.realpath( __file__ ) )
    test_dir = os.path.join( loc, 'function' )
    checked_list = []
    if type(test_list) == str and test_list.strip().lower() == 'all':
        all_files = os.listdir( test_dir )
        test_list = []
        for f in all_files:
            if f.startswith( 'test' ) and f.endswith( '.py' ):
               test_list.append(f)
    for test in test_list:
        test_path = os.path.join( test_dir, test )
        if os.path.isfile( test_path ):
            checked_list.append( test_path )
        else:
            print( 'cannot find {}'.format( test_path ) )
            return None
    return checked_list

def is_output_valid( filename, out_type ):
    if type( out_type ) != str or out_type.lower().strip() not in ['screen', 'file', 'none']:
        print( "summary output must be one of 'screen', 'file', or 'none'." )
        return False
    if out_type.lower().strip() == 'file':
        try:
            f = open( filename, 'w' )
            f.close()
        except Exception:
            print( 'unable to use filename {}'.format( filename ) )
            return False
    return True

def display( out_text, filename, out_type ):
    if out_type.lower().strip() == 'screen':
        print( out_text )
    elif out_type.lower().strip() == 'file':
        f = open( filename, 'w' )
        f.write( out_text )
        f.close()
    return None

