from test_config import IndexesBuildingQueryConfig, CmdlineSearchQueryConfig, Corpus, IndexesBuildingQueryTestConfig, CmdlineSearchQueryTestConfig
from test_handler import test_indexes_building, test_cmdline_search, print_indexes_building_test_results, print_cmdline_search_test_results

def simple_test() -> None:
    """ A simple indexes building and command-line search test. """
    indexes_building_test_results = test_indexes_building(
        IndexesBuildingQueryTestConfig(
        python_paths=['python'],
        build_speeds=['internal'],
        corpora=[Corpus('../corpora/bnc-100k.csv')],
        sorters=['internal'],
        indexes_building_query_configs=[IndexesBuildingQueryConfig()]
    ))
    print_indexes_building_test_results(
        test_results=indexes_building_test_results,
        write_to_csv=True,
        csv_filename='indexes_building_test_results.csv'
    )

    cmdline_search_test_results = test_cmdline_search(
        CmdlineSearchQueryTestConfig(
        python_paths=['python'],
        corpora=[Corpus('../corpora/bnc-100k.csv')],
        cmdline_search_query_configs=[CmdlineSearchQueryConfig()]
    ))
    print_cmdline_search_test_results(
        test_results=cmdline_search_test_results,
        write_to_csv=True,
        csv_filename='cmdline_search_test_results.csv'
    )

def comprehensive_test() -> None:
    """ A comprehensive indexes building and command-line search test for all possible default inputs. """
    full_indexes_building_test_results = test_indexes_building(IndexesBuildingQueryTestConfig())
    print_indexes_building_test_results(full_indexes_building_test_results)

    full_cmdline_search_test_results = test_cmdline_search(CmdlineSearchQueryTestConfig())
    print_cmdline_search_test_results(full_cmdline_search_test_results)

def main():
    simple_test()
    #comprehensive_test()

if __name__ == "__main__":
    main()
