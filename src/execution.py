""" Executing programs on the falconcode dataset.
This code was adapted from
https://github.com/openai/human-eval/blob/master/human_eval/execution.py
"""

from typing import Optional, Callable, Dict
import ast
import contextlib
import faulthandler
import io
import os
import multiprocessing
import platform
import signal
import tempfile

import src.utils.autograder
from src.utils.files import write


def check_correctness(problem: Dict, completion: str, timeout: float,
                      completion_id: Optional[int] = None) -> Dict:
    """
    Evaluates the functional correctness of a completion by running the test
    suite provided in the problem. 

    :param completion_id: an optional completion ID so we can match
        the results later even if execution finishes asynchronously.
    """

    def unsafe_execute():

        with create_tempdir():

            # These system calls are needed when cleaning up tempdir.
            import os
            import sys 
            import shutil

            rmtree = shutil.rmtree
            rmdir = os.rmdir
            chdir = os.chdir
            unlink = os.unlink

            # Disable functionalities that can make destructive changes to the test.
            reliability_guard()

            # adding the temp dir to the path such that autograder.py can be seen 
            sys.path.append("./")

            write(problem["id"] + ".py", problem["code"])
            write("autograder.py", get_autograder_code())
            exec_string = create_execution_string(problem["testcase"])
                        
            try:
                exec_globals = {}
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    with contextlib.redirect_stderr(stream):
                        with redirect_stdin(stream):
                            exec(exec_string, exec_globals)
                unit_test_result = stream.getvalue()
                score = get_unit_test_score(unit_test_result)
                result.append({"exec_result": "completed", "score": score, "text": unit_test_result})
                assert isinstance(score, float)

            except TimeoutException:
                result.append({"exec_result": "timed out", "score": 0, "text": unit_test_result})
            except BaseException as e:
                result.append({"exec_result": f"failed: {e}", "score": 0, "text": ""})
                # print(result[-1])
            
            # Needed for cleaning up.
            shutil.rmtree = rmtree
            os.rmdir = rmdir
            os.chdir = chdir
            os.unlink = unlink
            # remove the temp dir from the path 
            sys.path.pop()

    manager = multiprocessing.Manager()
    result = manager.list()

    p = multiprocessing.Process(target=unsafe_execute)
    p.start()
    p.join(timeout=timeout + 1)
    if p.is_alive():
        p.kill()

    if not result:
        result.append({"exec_result": "timed out", "score": 0, "text": ""})

    return result[0]


@contextlib.contextmanager
def time_limit(seconds: float):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.setitimer(signal.ITIMER_REAL, seconds)
    signal.signal(signal.SIGALRM, signal_handler)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


@contextlib.contextmanager
def swallow_io():
    stream = WriteOnlyStringIO()
    with contextlib.redirect_stdout(stream):
        with contextlib.redirect_stderr(stream):
            with redirect_stdin(stream):
                yield


@contextlib.contextmanager
def create_tempdir():
    with tempfile.TemporaryDirectory() as dirname:
        with chdir(dirname):
            yield dirname


class TimeoutException(Exception):
    pass


class WriteOnlyStringIO(io.StringIO):
    """ StringIO that throws an exception when it's read from """

    def read(self, *args, **kwargs):
        raise IOError

    def readline(self, *args, **kwargs):
        raise IOError

    def readlines(self, *args, **kwargs):
        raise IOError

    def readable(self, *args, **kwargs):
        """ Returns True if the IO object can be read. """
        return False


class redirect_stdin(contextlib._RedirectStream):  # type: ignore
    _stream = 'stdin'


@contextlib.contextmanager
def chdir(root):
    if root == ".":
        yield
        return
    cwd = os.getcwd()
    os.chdir(root)
    try:
        yield
    except BaseException as exc:
        raise exc
    finally:
        os.chdir(cwd)


def reliability_guard(maximum_memory_bytes: Optional[int] = None):
    """
    This disables various destructive functions and prevents the generated code
    from interfering with the test (e.g. fork bomb, killing other processes,
    removing filesystem files, etc.)

    WARNING
    This function is NOT a security sandbox. Untrusted code, including, model-
    generated code, should not be blindly executed outside of one. See the 
    Codex paper for more information about OpenAI's code sandbox, and proceed
    with caution.
    """

    if maximum_memory_bytes is not None:
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (maximum_memory_bytes, maximum_memory_bytes))
        resource.setrlimit(resource.RLIMIT_DATA, (maximum_memory_bytes, maximum_memory_bytes))
        if not platform.uname().system == 'Darwin':
            resource.setrlimit(resource.RLIMIT_STACK, (maximum_memory_bytes, maximum_memory_bytes))

    faulthandler.disable()

    import builtins
    builtins.exit = None
    builtins.quit = None

    import os
    os.environ['OMP_NUM_THREADS'] = '1'

    os.kill = None
    os.system = None
    os.putenv = None
    os.remove = None
    os.removedirs = None
    os.rmdir = None
    os.fchdir = None
    os.setuid = None
    os.fork = None
    os.forkpty = None
    os.killpg = None
    os.rename = None
    os.renames = None
    os.truncate = None
    os.replace = None
    os.unlink = None
    os.fchmod = None
    os.fchown = None
    os.chmod = None
    os.chown = None
    os.chroot = None
    os.fchdir = None
    os.lchflags = None
    os.lchmod = None
    os.lchown = None
    os.getcwd = None
    os.chdir = None

    import shutil
    shutil.rmtree = None
    shutil.move = None
    shutil.chown = None

    import subprocess # we need subprocess.Popen by the autograder module 
    #subprocess.Popen = None  # type: ignore

    __builtins__['help'] = None

    import sys
    sys.modules['ipdb'] = None
    sys.modules['joblib'] = None
    sys.modules['resource'] = None
    sys.modules['psutil'] = None
    sys.modules['tkinter'] = None



def create_execution_string(testcase):
    testcase = testcase.replace("from cs110 import autograder", "import autograder")
    testcase = testcase.replace("if __name__ == '__main__':", "")
    testcase = testcase.replace("result = test_passed()", "")
    testcase = testcase.replace('print("Unit Test Returned:", result)', "")
    testcase = testcase.strip()
    testcase = testcase + "\nresult = test_passed()\n"
    testcase = testcase + 'print("Unit Test Returned:", result)'
    
    return testcase

def get_autograder_code():
    """ Super dirty but temporary """
    with open(src.utils.autograder.__file__, "r") as fp:
        file_content = fp.read()
    return file_content

def get_unit_test_score(testcase_output):
    lines = testcase_output.splitlines()
    utr = [l for l in lines if l.startswith("Unit Test Returned:")]
    if utr:
        return float(utr[0].replace("Unit Test Returned:", "").strip())
    return 0.0