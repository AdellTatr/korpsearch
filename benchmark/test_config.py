import os
import re
from dataclasses import dataclass, field
from typing import NamedTuple, List, Optional
from itertools import product
from test_util import get_corpus_file_headers, format_corpus_headers_with_indices, format_query_features_with_commas

class PythonPathConfig:
    """ Configures Python interpreter paths for different environments. """
    def __init__(self):
        self.python = 'python'
        self.pypy = self.get_pypy_path()

    @staticmethod
    def get_pypy_path() -> str:
        pypy_home = os.environ.get('PyPy_Home')
        if not pypy_home:
            raise EnvironmentError("The 'PyPy_Home' environment variable is not set.")
        return os.path.join(pypy_home, 'python.exe')

    def get_python_paths(self) -> List[str]:
        return [self.python, self.pypy]

class IndexesBuildingQueryConfig(NamedTuple):
    """ Configures query indexes build types (i.e. features or templates) with their arguments. """
    build_type: str = '--features'
    build_arguments: List[str] = ['word', 'lemma', 'pos']
    max_dist: int = 2
    min_frequency: int = 0
    no_sentence_breaks: bool = False

class CmdlineSearchQueryConfig(NamedTuple):
    """ Configures command-line search query arguments. """
    query_arguments: str = '[pos="ART"] [lemma="small"] [pos="SUBST"]'
    print_format: str = 'kwic'
    start_index: int = 0
    results_num: int = 10
    end_index: int = start_index + results_num - 1
    features_to_show: str = format_query_features_with_commas(query_arguments)
    no_cache: bool = False
    no_sentence_breaks: bool = False
    internal_intersection: bool = False
    filter_results: bool = False

@dataclass
class Corpus:
    """ Represents a corpus. """
    path: str

    @property
    def name(self) -> str:
        return re.sub(r'\.csv(\.bz2)?$', '', self.path)

    @property
    def headers(self) -> List[str]:
        return get_corpus_file_headers(self.path)

@dataclass
class IndexesBuildingQueryTestConfig:
    """ Configures indexes building query test arguments. """
    python_paths: List[str] = field(default_factory=lambda: PythonPathConfig().get_python_paths())
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
                    build_arguments=corpus.headers if build_type == '--features' else format_corpus_headers_with_indices(corpus.headers),
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
    """ Configures command-line search query test arguments. """
    python_paths: List[str] = field(default_factory=lambda: PythonPathConfig().get_python_paths())
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
                    features_to_show=format_query_features_with_commas(query_argument),
                    no_cache=no_cache,
                    no_sentence_breaks=no_sentence_breaks,
                    internal_intersection=internal_intersection,
                    filter_results=filter_results
                )
                for query_argument in ['[pos="ART"] [lemma="small"] [pos="SUBST"]', '[pos="ART"] [lemma="big"] [pos="SUBST"]', '[lemma="be"] [pos="ART"] [pos="ADJ"] [pos="SUBST"]', '[pos="ADJ"] [lemma="cut" pos="VERB"]']
                for print_format in ['kwic', 'json']
                for no_cache, no_sentence_breaks, internal_intersection, filter_results in product([True, False], repeat=4)
            ]
