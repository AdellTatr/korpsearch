from typing import List, Tuple, Callable
from prettytable import PrettyTable
import csv
import os
from test_util import time_function, get_benchmark_absolute_path
from test_command_builder import build_indexes, build_inverted_indexes, clean_all, build_java_arrays, build_fast_intersection, run_cmdline_search_query
from test_config import IndexesBuildingQueryTestConfig, CmdlineSearchQueryTestConfig, TestResultBase, IndexesBuildingTestResult, CmdlineSearchTestResult

def execute_test_cycle(
        test_result: TestResultBase,
        build_functions: List[Callable],
        test_function: Callable
    ) -> int:
    """ Executes a build process and then tests performance. """
    return_codes = []
    for build_function in build_functions:
        return_codes.append(build_function())
    test_function_return_code, execution_time = test_function(test_result)
    test_result.execution_time = execution_time
    return_codes.append(test_function_return_code)
    return sum(abs(return_code) for return_code in return_codes)

@time_function
def test_indexes_building_performance(test_result: IndexesBuildingTestResult) -> int:
    """ Tests the performance of indexes building (basic and inverted). """
    build_indexes_return_code = build_indexes(test_result.python_path, test_result.corpus.path)
    build_inverted_indexes_return_code = build_inverted_indexes(test_result.python_path, test_result.corpus.path, test_result.indexes_building_query_config, test_result.sorter)
    return abs(build_indexes_return_code) + abs(build_inverted_indexes_return_code)

@time_function
def test_cmdline_search_performance(test_result: CmdlineSearchTestResult) -> int:
    """ Tests the performance of a command-line search query. """
    return run_cmdline_search_query(test_result.python_path, test_result.corpus.name, test_result.cmdline_search_query_config)

def perform_indexes_building_and_testing_cycle(test_result: IndexesBuildingTestResult) -> int:
    """ Performs a full cycle of indexes building and testing for the given configuration. """
    build_functions = []
    if test_result.sorter == 'java':
        build_functions.append(build_java_arrays)
    if test_result.build_speed == 'fast-intersection':
        build_functions.append(build_fast_intersection)
    return execute_test_cycle(test_result, build_functions, test_indexes_building_performance)

def perform_cmdline_searching_and_testing_cycle(test_result: CmdlineSearchTestResult) -> int:
    """ Performs a full cycle of command-line searching and testing for the given configuration. """
    build_functions = []
    if not test_result.cmdline_search_query_config.internal_intersection:
        build_functions.append(build_fast_intersection)
    return execute_test_cycle(test_result, build_functions, test_cmdline_search_performance)

def test_indexes_building(indexes_building_query_test_config: IndexesBuildingQueryTestConfig) -> List[IndexesBuildingTestResult]:
    """ Tests a list of indexes building configurations on a corpus and records the results. """
    test_results = []
    for python_path in indexes_building_query_test_config.python_paths:
        for build_speed in indexes_building_query_test_config.build_speeds:
            for corpus in indexes_building_query_test_config.corpora:
                for indexes_building_query_config in indexes_building_query_test_config.indexes_building_query_configs:
                    for sorter in indexes_building_query_test_config.sorters:
                        if clean_all() == 0:
                            test_result = IndexesBuildingTestResult(python_path=python_path, build_speed=build_speed, corpus=corpus, indexes_building_query_config=indexes_building_query_config, sorter=sorter, execution_time=0.0)
                            if perform_indexes_building_and_testing_cycle(test_result) == 0:
                                test_results.append(test_result)
    return test_results

def test_cmdline_search(cmdline_search_query_test_config: CmdlineSearchQueryTestConfig) -> List[CmdlineSearchTestResult]:
    """ Tests a list of command-line searching configurations on a corpus and records the results. """
    test_results = []
    for python_path in cmdline_search_query_test_config.python_paths:
        for corpus in cmdline_search_query_test_config.corpora:
            for cmdline_search_query_config in cmdline_search_query_test_config.cmdline_search_query_configs:
                test_result = CmdlineSearchTestResult(python_path=python_path, corpus=corpus, cmdline_search_query_config=cmdline_search_query_config, execution_time=0.0)
                if perform_cmdline_searching_and_testing_cycle(test_result) == 0:
                    test_results.append(test_result)
    return test_results

def prepare_indexes_building_row(test_result: IndexesBuildingTestResult) -> Tuple[List[str], List[str]]:
    """ Prepares a row of data and headers for an IndexesBuildingTestResult object. """
    headers = ['Python Path', 'Build Speed', 'Corpus Path', 'Build Type', 'Build Arguments', 'Maximum Distance', 'Minimum Frequency', 'No Sentence Breaks', 'Sorter', 'Execution Time']
    row = [
        test_result.python_path_str,
        test_result.build_speed,
        test_result.corpus_path_str,
        test_result.build_type_str,
        test_result.build_arguments_str,
        test_result.max_dist_str,
        test_result.min_frequency_str,
        test_result.no_sentence_breaks_str,
        test_result.sorter,
        test_result.execution_time_str
    ]
    return headers, row

def prepare_cmdline_search_row(test_result: CmdlineSearchTestResult) -> Tuple[List[str], List[str]]:
    """ Prepares a row of data and headers for a CmdlineSearchTestResult object. """
    headers = ['Python Path', 'Corpus Path', 'Query Arguments', 'Print Format', 'Start Index', 'Results Number', 'End Index', 'Features to Show', 'No Cache', 'No Sentence Breaks', 'Internal Intersection', 'Filter Results', 'Execution Time']
    row = [
        test_result.python_path_str,
        test_result.corpus_path_str,
        test_result.query_arguments_str,
        test_result.print_format_str,
        test_result.start_index_str,
        test_result.results_num_str,
        test_result.end_index_str,
        test_result.features_to_show_str,
        test_result.no_cache_str,
        test_result.no_sentence_breaks_str,
        test_result.internal_intersection_str,
        test_result.filter_results_str,
        test_result.execution_time_str,
    ]
    return headers, row

def print_test_results(
        test_results: List[TestResultBase],
        row_preparation_function: Callable[[TestResultBase], Tuple[List[str], List[str]]],
        write_to_csv: bool = False,
        csv_filename: str = "test_results.csv"
    ) -> None:
    """ Prints test results in a formatted table or writes them to a CSV file.
    Assumes the first row contains the headers. """
    if not test_results:
        return

    data_with_headers = [row_preparation_function(result) for result in test_results]
    headers, data = data_with_headers[0][0], [row[1] for row in data_with_headers]

    if write_to_csv and csv_filename:
        with open(os.path.join(get_benchmark_absolute_path(), csv_filename), mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(data)
    else:
        table = PrettyTable()
        table.field_names = headers
        for row in data:
            table.add_row(row)
        print(table)

def print_indexes_building_test_results(
        test_results: IndexesBuildingTestResult,
        write_to_csv: bool=True,
        csv_filename: str='indexes_building_test_results.csv'
    ) -> None:
    """ Prints indexes building test results in a formatted table or writes them to a CSV file. """
    print_test_results(test_results=test_results, row_preparation_function=prepare_indexes_building_row, write_to_csv=write_to_csv, csv_filename=csv_filename)

def print_cmdline_search_test_results(
        test_results: CmdlineSearchTestResult,
        write_to_csv: bool=True,
        csv_filename: str='cmdline_search_test_results.csv'
    ) -> None:
    """ Prints command-line search test results in a formatted table or writes them to a CSV file. """
    print_test_results(test_results=test_results, row_preparation_function=prepare_cmdline_search_row, write_to_csv=write_to_csv, csv_filename=csv_filename)
