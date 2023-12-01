import os
import re
import bz2
from dataclasses import dataclass, field
from typing import List, Optional
from itertools import product
from test_util import is_in_benchmark_directory

@dataclass
class PythonPathConfig:
    """ Configures Python and PyPy interpreters paths. """
    python: str = field(default_factory=lambda: 'python')
    pypy: Optional[str] = None

    def __post_init__(self):
        if self.pypy is None:
            self.pypy = self.get_pypy_path()

    @property
    def python_paths(self) -> list[str]:
        return [self.python, self.pypy]

    @staticmethod
    def get_pypy_path() -> str:
        """ Retrieves the path to the PyPy interpreter from the 'PyPy_Home' environment variable. """
        pypy_home = os.environ.get('PyPy_Home')
        if not pypy_home:
            raise EnvironmentError("The 'PyPy_Home' environment variable is not set.")
        return os.path.join(pypy_home, 'python.exe')

@dataclass
class IndexesBuildingQueryConfig:
    build_type: str = field(default_factory=lambda: '--features')
    max_dist: int = field(default_factory=lambda: 2)
    min_frequency: int = field(default_factory=lambda: 0)
    no_sentence_breaks: bool = field(default_factory=lambda: False)
    build_arguments: Optional[List[str]] = None

    def __post_init__(self):
        if self.build_arguments is None:
            if self.build_type == '--features':
                self.build_arguments = ['word', 'lemma', 'pos']
            else:
                self.build_arguments = self.format_corpus_headers_with_indices(['word', 'lemma', 'pos'])

    @staticmethod
    def format_corpus_headers_with_indices(build_arguments: List[str]) -> str:
        """
        Appends indices to build arguments and joins them into a string, i.e., from type 'features' to type 'templates' arguments.
        Example:
            Input: ['word', 'pos', 'lemma']
            Output: 'word-0+pos-1+lemma-2'
        """
        return '+'.join([f"{feature}-{index}" for index, feature in enumerate(build_arguments)])

@dataclass
class CmdlineSearchQueryConfig():
    """ Configures command-line search query arguments. """
    query_arguments: str = field(default_factory=lambda: '[pos="ART"] [lemma="small"] [pos="SUBST"]')
    print_format: str = field(default_factory=lambda: 'kwic')
    start_index: int = field(default_factory=lambda: 0)
    results_num: int = field(default_factory=lambda: 10)
    no_cache: bool = field(default_factory=lambda: False)
    no_sentence_breaks: bool = field(default_factory=lambda: False)
    internal_intersection: bool = field(default_factory=lambda: False)
    filter_results: bool = field(default_factory=lambda: False)
    end_index: Optional[int] = None
    features_to_show: Optional[str] = None

    def __post_init__(self):
        if self.end_index is None:
            self.end_index = self.start_index + self.results_num - 1

        if self.features_to_show is None:
            self.features_to_show = self.format_query_features_with_commas(self.query_arguments)

    @staticmethod
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

@dataclass
class Corpus:
    """ Represents a corpus. """
    path: str

    @property
    def name(self) -> str:
        return re.sub(r'\.csv(\.bz2)?$', '', self.path)

    @property
    def headers(self) -> List[str]:
        return self.get_corpus_file_headers(self.path)

    @staticmethod
    def get_corpus_file_headers(path: str) -> List[str]:
        """Extracts the headers of a given corpus file. Supports CSV and BZ2 compressed CSV files."""
        if is_in_benchmark_directory():
            adjusted_path = os.path.join('..', path)
        else:
            adjusted_path = path.replace('../', './')

        if adjusted_path.endswith('.bz2'):
            with bz2.open(adjusted_path, mode='rt', encoding='utf-8') as file:
                header_line = next(file)
        else:
            with open(adjusted_path, mode='r', encoding='utf-8') as file:
                header_line = next(file)

        return [header for header in header_line.strip().split('\t') if header]

@dataclass
class IndexesBuildingQueryTestConfig:
    """ Configures indexes building query test arguments. The default values are all possible values. """
    python_paths: List[str] = field(default_factory=lambda: PythonPathConfig().python_paths)
    build_speeds: List[str] = field(default_factory=lambda: ['internal', 'fast-intersection'])
    corpora: List[Corpus] = field(default_factory=lambda: [
        Corpus(path=path)
        for path in [
            '../corpora/bnc-100k.csv', '../corpora/bnc-01M.csv.bz2',
            '../corpora/bnc-02M.csv.bz2', '../corpora/bnc-05M.csv.bz2',
            '../corpora/talbanken.csv.bz2'
        ]
    ])
    sorters: List[str] = field(default_factory=lambda: ['tmpfile', 'internal', 'java', 'lmdb'])
    indexes_building_query_configs: Optional[List[IndexesBuildingQueryConfig]] = None

    def __post_init__(self):
        if self.indexes_building_query_configs is None:
            self.indexes_building_query_configs = [
                IndexesBuildingQueryConfig(
                    build_type=build_type,
                    build_arguments=corpus.headers if build_type == '--features' else IndexesBuildingQueryConfig.format_corpus_headers_with_indices(corpus.headers),
                    max_dist=max_dist,
                    min_frequency=min_frequency,
                    no_sentence_breaks=no_sentence_breaks
                )
                for build_type in ['--features', '--templates']
                for corpus in self.corpora
                for max_dist in list(range(2, 6))
                for min_frequency in list(range(0, 3))
                for no_sentence_breaks in [True, False]
            ]

@dataclass
class CmdlineSearchQueryTestConfig:
    """ Configures command-line search query test arguments. The default values are all possible values. """
    python_paths: List[str] = field(default_factory=lambda: PythonPathConfig().python_paths)
    corpora: List[Corpus] = field(default_factory=lambda: [
        Corpus(path=path)
        for path in [
            '../corpora/bnc-100k.csv', '../corpora/bnc-01M.csv.bz2',
            '../corpora/bnc-02M.csv.bz2', '../corpora/bnc-05M.csv.bz2',
            '../corpora/talbanken.csv.bz2'
        ]
    ])
    cmdline_search_query_configs: Optional[List[CmdlineSearchQueryConfig]] = None

    def __post_init__(self):
        if self.cmdline_search_query_configs is None:
            self.cmdline_search_query_configs = [
                CmdlineSearchQueryConfig(
                    query_arguments=query_argument,
                    print_format=print_format,
                    start_index=0,
                    results_num=20,
                    end_index=19,
                    no_cache=no_cache,
                    no_sentence_breaks=no_sentence_breaks,
                    internal_intersection=internal_intersection,
                    filter_results=filter_results
                )
                for query_argument in ['[pos="ART"] [lemma="small"] [pos="SUBST"]', '[pos="ART"] [lemma="big"] [pos="SUBST"]', '[lemma="be"] [pos="ART"] [pos="ADJ"] [pos="SUBST"]', '[pos="ADJ"] [lemma="cut" pos="VERB"]']
                for print_format in ['kwic', 'json']
                for no_cache, no_sentence_breaks, internal_intersection, filter_results in product([True, False], repeat=4)
            ]

@dataclass
class TestResultBase:
    """ Represents the base structure for storing test results including paths and execution time. """
    python_path: str = field(default_factory=lambda: PythonPathConfig.python)
    corpus: Corpus = field(default_factory=lambda: Corpus('../corpora/bnc-100k.csv'))
    execution_time: float = field(default_factory=lambda: 0.0)

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
        return self.corpus.path.replace('../', '')

    @property
    def execution_time_str(self) -> str:
        return f"{self.execution_time:.2f}"

@dataclass
class IndexesBuildingTestResult(TestResultBase):
    """ Stores the results of indexes building tests along with specific configuration details. """
    build_speed: str = field(default_factory=lambda: 'internal')
    sorter: str = field(default_factory=lambda: 'internal')
    indexes_building_query_config: IndexesBuildingQueryConfig = field(default_factory=lambda: IndexesBuildingQueryConfig())

    @property
    def build_type_str(self) -> str:
        return self.indexes_building_query_config.build_type.replace('--', '')

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
    cmdline_search_query_config: CmdlineSearchQueryConfig = field(default_factory=lambda: CmdlineSearchQueryConfig())

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
