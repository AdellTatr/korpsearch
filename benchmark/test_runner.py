from test_suite import basic_indexes_building_and_search_test, complex_indexes_building_and_search_test, exhaustive_indexes_building_and_search_test

def run_tests():
    """ Runs the chosen collection of tests. """
    basic_indexes_building_and_search_test()
    #complex_indexes_building_and_search_test()
    #exhaustive_indexes_building_and_search_test()

if __name__ == "__main__":
    run_tests()
