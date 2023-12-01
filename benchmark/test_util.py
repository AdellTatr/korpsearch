import time
import subprocess
import os
from functools import wraps
from typing import Callable, Tuple, Any, List

def time_function(f: Callable) -> Callable:
    """Decorator to measure execution time of a function."""
    @wraps(f)
    def wrap(*args, **kwargs) -> Tuple[Any, float]:
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time
    return wrap

def is_in_benchmark_directory() -> bool:
    """Determine if the current directory is the 'benchmark' folder."""
    return os.path.basename(os.getcwd()) == 'benchmark'

def get_benchmark_absolute_path() -> str:
    """Get the absolute path of the 'benchmark' directory."""
    current_dir = os.getcwd()
    return current_dir if is_in_benchmark_directory() else os.path.join(current_dir, 'benchmark')

def run_subprocess(args: List[str]) -> int:
    """Runs a subprocess after adjusting the command based on the current directory."""
    if is_in_benchmark_directory():
        file_dir = '..'
    else:
        file_dir = '.'
        args = [arg.replace('../', './') if arg.startswith('../') else arg for arg in args]

    if args[0] == 'make':
        args = ['make', '-C', file_dir] + args[1:]

    return_code = subprocess.run(args, text=True, check=False).returncode

    if return_code != 0:
        print(f"Programme exited with status code {return_code} while executing '{' '.join(args)}'")

    return return_code
