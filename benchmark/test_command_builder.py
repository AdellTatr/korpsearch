from test_config import IndexesBuildingQueryConfig, CmdlineSearchQueryConfig
from test_util import run_subprocess

def build_indexes(python_path: str, corpus_path: str) -> None:
    """ Builds basic indexes for given corpus. """
    run_subprocess([
        python_path,
        '../build_indexes.py',
        '--corpus',
        corpus_path,
        '--corpus-index',
        '--silent'
    ])

def build_inverted_indexes(
        python_path: str,
        corpus_path: str,
        indexes_building_query_config: IndexesBuildingQueryConfig,
        sorter: str
    ) -> None:
    """ Builds inverted indexes for given corpus based on configuration. """
    args = [
        python_path,
        '../build_indexes.py',
        '--corpus',
        corpus_path,
        indexes_building_query_config.build_type
    ] + \
        indexes_building_query_config.build_arguments + \
    [
        '--max-dist',
        str(indexes_building_query_config.max_dist)
    ] + \
    [
        '--min-frequency',
        str(indexes_building_query_config.min_frequency)
    ] + \
    [
        '--sorter',
        sorter,
        '--silent'
    ]
    if indexes_building_query_config.no_sentence_breaks:
        args += ['--no-sentence-breaks']
    run_subprocess(args)

def build_java_arrays() -> None:
    """ Builds the Java implementation of Disk Fixed Size Arrays (for 'java' sorting). """
    run_subprocess(['make', 'java-arrays'])

def build_fast_intersection() -> None:
    """ Builds the faster intersection module using Cython. """
    run_subprocess(['make', 'fast-intersection'])

def clean_all() -> None:
    """ Cleans all built components. """
    run_subprocess(['make', 'clean-all'])

def run_cmdline_search_query(
        python_path: str,
        corpus_path: str,
        cmdline_search_query_config: CmdlineSearchQueryConfig
    ) -> None:
    """ Executes command-line search query on given corpus based on configuration. """
    args = [
        python_path,
        '../search_cmdline.py',
        '--corpus',
        corpus_path,
        '--query',
        cmdline_search_query_config.query_arguments,
        '--print',
        cmdline_search_query_config.print_format,
        '--start', str(cmdline_search_query_config.start_index),
        '--num', str(cmdline_search_query_config.results_num),
        '--end', str(cmdline_search_query_config.end_index),
        '--show', cmdline_search_query_config.features_to_show
    ]
    if cmdline_search_query_config.no_cache:
        args += ['--no-cache']
    if cmdline_search_query_config.no_sentence_breaks:
        args += ['--no-sentence-breaks']
    if cmdline_search_query_config.internal_intersection:
        args += ['--internal-intersection']
    if cmdline_search_query_config.filter_results:
        args += ['--filter']
    run_subprocess(args)
