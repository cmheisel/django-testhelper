from django.test.simple import *

def quieter(test_labels, verbosity=1, interactive=True, extra_tests=[]):
    """
    Note: Adapted from django.test.simple.run_tests, lowering verbosity level of db creation/teardown
    
    Run the unit tests for all the test labels in the provided list.
    Labels must be of the form:
     - app.TestClass.test_method
        Run a single specific test method
     - app.TestClass
        Run all the test methods in a given class
     - app
        Search for doctests and unittests in the named application.

    When looking for tests, the test runner will look in the models and
    tests modules for the application.
    
    A list of 'extra' tests may also be provided; these tests
    will be added to the test suite.
    
    Returns the number of tests that failed.
    """
    db_verbosity = verbosity - 1
    if db_verbosity < 0: db_verbosity = 0
    
    setup_test_environment()
    
    settings.DEBUG = False    
    suite = unittest.TestSuite()
    
    if test_labels:
        for label in test_labels:
            if '.' in label:
                suite.addTest(build_test(label))
            else:
                app = get_app(label)
                suite.addTest(build_suite(app))
    else:
        for app in get_apps():
            suite.addTest(build_suite(app))
    
    for test in extra_tests:
        suite.addTest(test)

    old_name = settings.DATABASE_NAME
    from django.db import connection
    connection.creation.create_test_db(db_verbosity, autoclobber=not interactive)
    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
    connection.creation.destroy_test_db(old_name, db_verbosity)
    
    teardown_test_environment()
    
    return len(result.failures) + len(result.errors)