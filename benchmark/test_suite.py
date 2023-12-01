from test_config import IndexesBuildingQueryConfig, CmdlineSearchQueryConfig, Corpus, IndexesBuildingQueryTestConfig, CmdlineSearchQueryTestConfig
from test_handler import test_indexes_building, test_cmdline_search, print_indexes_building_test_results, print_cmdline_search_test_results

def basic_indexes_building_test() -> None:
    """
    Conducts a basic test of indexes building and prints the results.
    This test uses one value for each argument.
    """
    indexes_building_test_results = test_indexes_building(
        IndexesBuildingQueryTestConfig(
        python_paths=['python'],
        build_speeds=['internal'],
        corpora=[Corpus('../corpora/bnc-100k.csv')],
        sorters=['internal'],
        indexes_building_query_configs=[IndexesBuildingQueryConfig()]
    ))
    print_indexes_building_test_results(test_results=indexes_building_test_results)

def basic_search_test() -> None:
    """
    Conducts a basic test of command-line search and prints the results.
    This test uses one value for each argument.
    """
    cmdline_search_test_results = test_cmdline_search(
        CmdlineSearchQueryTestConfig(
        python_paths=['python'],
        corpora=[Corpus('../corpora/bnc-100k.csv')],
        cmdline_search_query_configs=[CmdlineSearchQueryConfig()]
    ))
    print_cmdline_search_test_results(test_results=cmdline_search_test_results)

def basic_indexes_building_and_search_test() -> None:
    """
    Conducts a basic test of indexes building and command-line search and prints the results.
    This test uses one value for each argument.
    """
    basic_indexes_building_test()
    basic_search_test()

def complex_indexes_building_test() -> None:
    """
    Conducts a complex test of indexes building and prints the results.
    This test uses an extensive list of values for each argument on a single corpus.
    """
    indexes_building_test_results = test_indexes_building(IndexesBuildingQueryTestConfig(corpora=[Corpus('../corpora/bnc-100k.csv')]))

    print_indexes_building_test_results(test_results=indexes_building_test_results)

def complex_search_test() -> None:
    """
    Conducts a complex test of command-line search and prints the results.
    This test uses an extensive list of values for each argument on a single corpus.
    """
    cmdline_search_test_results = test_cmdline_search(CmdlineSearchQueryTestConfig(corpora=[Corpus('../corpora/bnc-100k.csv')]))
    print_cmdline_search_test_results(test_results=cmdline_search_test_results)

def complex_indexes_building_and_search_test() -> None:
    """
    Conducts a complex test of indexes building and command-line search and prints the results.
    This test uses an extensive list of values for each argument on a single corpus.
    """
    complex_indexes_building_test()
    complex_search_test()

def exhaustive_indexes_building_test() -> None:
    """
    Conducts a comprehensive test of indexes building and prints the results.
    This test uses default (all) values for all arguments.
    """
    full_indexes_building_test_results = test_indexes_building(IndexesBuildingQueryTestConfig())
    print_indexes_building_test_results(full_indexes_building_test_results)

def exhaustive_search_test() -> None:
    """
    Conducts a comprehensive test of command-line search and prints the results.
    This test uses default (all) values for all arguments.
    """
    full_cmdline_search_test_results = test_cmdline_search(CmdlineSearchQueryTestConfig())
    print_cmdline_search_test_results(full_cmdline_search_test_results)

def exhaustive_indexes_building_and_search_test() -> None:
    """
    Conducts a comprehensive test of indexes building and command-line search and prints the results.
    This test uses default (all) values for all arguments.
    """
    exhaustive_indexes_building_test()
    exhaustive_search_test()
