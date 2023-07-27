""" Copy of a set of utility functions that were used in the FalconCode project. """

import math
from unittest.mock import patch
from io import StringIO
from contextlib import (
    redirect_stdout, redirect_stderr
)

from src.utils.code import does_compile

def run_script(filepath, input_list, b=False):
    """ 
    Run a generic python program on the set of 
    inputs given in input list. 
    """

    with open(filepath, "r") as fp:
        student_solution = fp.read()
        
    output, error = "", ""
    with patch('builtins.input') as input_mock:
        input_mock.side_effect = input_list
        
        try:
            exec_globals = {}
            output_io = StringIO()
            with redirect_stdout(output_io):
                exec(student_solution, exec_globals)

        except BaseException as e:
            error = str(e)

    output = output_io.getvalue()

    return output, error 

def compare_strings(outputs, expected_outputs):
    """ 
    Returns the number of matching elements at the same positions
    among two lists
    """
    return sum([o == eo for o, eo in zip(outputs, expected_outputs)])


def equals(a, b, abs_tol=0.0):
    if is_float(a) and is_float(b):
        return math.isclose(a, b, abs_tol=abs_tol)
    return a == b


def code_compiles(filepath):
    """ 
    Run a generic python program on the set of 
    inputs given in input list. 
    """

    with open(filepath, "r") as fp:
        student_solution = fp.read()
        
    return does_compile(student_solution)


def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False 