""" Copy of a set of utility functions that were used in the FalconCode project. """

import builtins
from unittest.mock import patch
from io import StringIO
from contextlib import (
    redirect_stdout, redirect_stderr
)

def run_script(filepath, input_list):
    """ 
    Run a generic python program on the set of 
    inputs given in input list. 
    """

    with open(filepath, "r") as fp:
        student_solution = fp.read()
        
    output, error = "", ""
    with patch('builtins.input') as input_mock:
        input_mock.side_effect = input_list
        
        exec_globals = {}
        output_io = StringIO()
        error_io = StringIO()
        with redirect_stdout(output_io):
            with redirect_stderr(error_io):
                exec(student_solution, exec_globals)

    output = output_io.getvalue()
    error = error_io.getvalue()
    
    return output, error 

def compare_strings(outputs, expected_outputs):
    """ 
    Returns the number of matching elements at the same positions
    among two lists
    """
    return sum([o == eo for o, eo in zip(outputs, expected_outputs)])
