import time
import subprocess
import os
import re
import bz2
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

def run_subprocess(args: List[str]) -> None:
    """Runs a subprocess after adjusting the command based on the current directory."""
    if is_in_benchmark_directory():
        file_dir = '..'
    else:
        file_dir = '.'
        args = [arg.replace('../', './') if arg.startswith('../') else arg for arg in args]

    if args[0] == 'make':
        args = ['make', '-C', file_dir] + args[1:]

    try:
        subprocess.run(args, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing {' '.join(e.cmd)}: {e}")
        raise

def get_corpus_file_headers(file_path: str) -> List[str]:
    """Extracts the headers of a given corpus file. Supports CSV and BZ2 compressed CSV files."""
    if is_in_benchmark_directory():
        adjusted_path = os.path.join('..', file_path)
    else:
        adjusted_path = file_path.replace('../', './')

    if adjusted_path.endswith('.bz2'):
        with bz2.open(adjusted_path, mode='rt', encoding='utf-8') as file:
            header_line = next(file)
    else:
        with open(adjusted_path, mode='r', encoding='utf-8') as file:
            header_line = next(file)

    headers = [header for header in header_line.strip().split('\t') if header]

    return headers

def format_corpus_headers_with_indices(corpus_headers: List[str]) -> str:
    """
    Appends indices to corpus headers and joins them into a string, i.e., from type 'features' to type 'templates' arguments.
    Example:
        Input: ['word', 'pos', 'lemma']
        Output: 'word-0+pos-1+lemma-2'
    """
    return '+'.join([f"{feature}-{index}" for index, feature in enumerate(corpus_headers)])

def format_query_features_with_commas(query_arguments: str) -> str:
    """
    Extracts and formats features from a query arguments string. Returns a string of comma-separated features.
    Example:
        Input: '[pos="ART"] [lemma="small"] [pos="SUBST"]'
        Output: 'lemma,pos'
    """
    comma_separated_features = ''
    features = re.findall(r'\b(\w+)="[^"]+"', query_arguments)
    if features:
        unique_features = set(features)
        comma_separated_features = ','.join(unique_features)
    return comma_separated_features
