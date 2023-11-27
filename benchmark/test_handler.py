from dataclasses import dataclass
from typing import List, Tuple, Callable, TypeVar
from prettytable import PrettyTable
import csv
import os
from test_util import time_function, get_benchmark_absolute_path
from test_command_builder import build_indexes, build_inverted_indexes, clean_all, build_java_arrays, build_fast_intersection, run_cmdline_search_query
from test_config import IndexesBuildingQueryConfig, CmdlineSearchQueryConfig, IndexesBuildingQueryTestConfig, CmdlineSearchQueryTestConfig

@dataclass
class TestResultBase:
    """ Represents the base structure for storing test results including paths and execution time. """
    python_path: str
    corpus_path: str
    execution_time: float

    def __post_init__(self):
        try:
            self.execution_time = float(self.execution_time)
        except ValueError:
            raise TypeError("Execution time must be a numeric value")

        if self.execution_time < 0:
            raise ValueError("Execution time cannot be negative")

    @property
    def python_path_str(self) -> str:
        return 'python' if self.python_path == 'python' else 'pypy'

    @property
    def corpus_path_str(self) -> str:
        return self.corpus_path.replace('../', '')

    @property
    def execution_time_str(self) -> str:
        return f"{self.execution_time:.2f}"

@dataclass
class IndexesBuildingTestResult(TestResultBase):
    """ Stores the results of indexes building tests along with specific configuration details. """
    build_speed: str
    indexes_building_query_config: IndexesBuildingQueryConfig
    sorter: str

    @property
    def build_type_str(self) -> str:
        return 'features' if self.indexes_building_query_config.build_type == '--features' else 'templates'

    @property
    def build_arguments_str(self) -> str:
        return ', '.join(self.indexes_building_query_config.build_arguments)

    @property
    def max_dist_str(self) -> str:
        return str(self.indexes_building_query_config.max_dist)

    @property
    def min_frequency_str(self) -> str:
        return str(self.indexes_building_query_config.min_frequency)

    @property
    def no_sentence_breaks_str(self) -> str:
        return str(self.indexes_building_query_config.no_sentence_breaks)

@dataclass
class CmdlineSearchTestResult(TestResultBase):
    """ Stores the results of  command-line search tests along with specific configuration details. """
    cmdline_search_query_config: CmdlineSearchQueryConfig

    @property
    def query_arguments_str(self) -> str:
        return self.cmdline_search_query_config.query_arguments

    @property
    def print_format_str(self) -> str:
        return self.cmdline_search_query_config.print_format

    @property
    def start_index_str(self) -> str:
        return str(self.cmdline_search_query_config.start_index)

    @property
    def results_num_str(self) -> str:
        return str(self.cmdline_search_query_config.results_num)

    @property
    def end_index_str(self) -> str:
        return str(self.cmdline_search_query_config.end_index)

    @property
    def features_to_show_str(self) -> str:
        return self.cmdline_search_query_config.features_to_show.replace(',', ', ')

    @property
    def no_cache_str(self) -> str:
        return str(self.cmdline_search_query_config.no_cache)

    @property
    def no_sentence_breaks_str(self) -> str:
        return str(self.cmdline_search_query_config.no_sentence_breaks)

    @property
    def internal_intersection_str(self) -> str:
        return str(self.cmdline_search_query_config.internal_intersection)

    @property
    def filter_results_str(self) -> str:
        return str(self.cmdline_search_query_config.filter_results)

def execute_test_cycle(
        test_result: TestResultBase,
        build_functions: List[Callable],
        test_function: Callable
    ) -> None:
    """ Executes a build process and then tests performance. """
    for build_function in build_functions:
        build_function()
    _, execution_time = test_function(test_result)
    test_result.execution_time = execution_time

@time_function
def test_indexes_building_performance(test_result: IndexesBuildingTestResult) -> None:
    """ Tests the performance of indexes building (basic and inverted). """
    build_indexes(test_result.python_path, test_result.corpus_path)
    build_inverted_indexes(test_result.python_path, test_result.corpus_path, test_result.indexes_building_query_config, test_result.sorter)

@time_function
def test_cmdline_search_performance(test_result: CmdlineSearchTestResult) -> None:
    """ Tests the performance of a command-line search query. """
    run_cmdline_search_query(test_result.python_path, test_result.corpus_path, test_result.cmdline_search_query_config)

def perform_indexes_building_and_testing_cycle(test_result: IndexesBuildingTestResult) -> None:
    """ Performs a full cycle of indexes building and testing for the given configuration. """
    build_functions = []
    if test_result.sorter == 'java':
        build_functions.append(build_java_arrays)
    if test_result.build_speed == 'fast-intersection':
        build_functions.append(build_fast_intersection)
    execute_test_cycle(test_result, build_functions, test_indexes_building_performance)

def perform_cmdline_searching_and_testing_cycle(test_result: CmdlineSearchTestResult) -> None:
    """ Performs a full cycle of command-line searching and testing for the given configuration. """
    build_functions = []
    if not test_result.cmdline_search_query_config.internal_intersection:
        build_functions.append(build_fast_intersection)
    execute_test_cycle(test_result, build_functions, test_cmdline_search_performance)

def test_indexes_building(indexes_building_query_test_config: IndexesBuildingQueryTestConfig) -> List[IndexesBuildingTestResult]:
    """ Tests a list of indexes building configurations on a corpus and records the results. """
    test_results = []
    for python_path in indexes_building_query_test_config.python_paths:
        for build_speed in indexes_building_query_test_config.build_speeds:
            for corpus in indexes_building_query_test_config.corpora:
                for indexes_building_query_config in indexes_building_query_test_config.indexes_building_query_configs:
                    for sorter in indexes_building_query_test_config.sorters:
                        clean_all()
                        test_result = IndexesBuildingTestResult(python_path=python_path, build_speed=build_speed, corpus_path=corpus.path, indexes_building_query_config=indexes_building_query_config, sorter=sorter, execution_time=0.0)
                        perform_indexes_building_and_testing_cycle(test_result)
                        test_results.append(test_result)
    return test_results

def test_cmdline_search(cmdline_search_query_test_config: CmdlineSearchQueryTestConfig) -> List[CmdlineSearchTestResult]:
    """ Tests a list of command-line searching configurations on a corpus and records the results. """
    test_results = []
    for python_path in cmdline_search_query_test_config.python_paths:
        for corpus in cmdline_search_query_test_config.corpora:
            for cmdline_search_query_config in cmdline_search_query_test_config.cmdline_search_query_configs:
                test_result = CmdlineSearchTestResult(python_path=python_path, corpus_path=corpus.name, cmdline_search_query_config=cmdline_search_query_config, execution_time=0.0)
                perform_cmdline_searching_and_testing_cycle(test_result)
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
