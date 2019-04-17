import unittest
from Partials.RecordTargetTest import RecordTargetTest
from Partials.ReplacementOfTest import ReplacementOfTest

if __name__ == '__main__':
    #suite = unittest.TestLoader().loadTestsFromTestCase(RecordTargetTest)
    #unittest.TextTestRunner(verbosity=2).run(suite)

    test_classes_to_run = [RecordTargetTest, ReplacementOfTest]

    loader = unittest.TestLoader()

    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    big_suite = unittest.TestSuite(suites_list)

    # runner = unittest.TextTestRunner()
    # results = runner.run(big_suite)
    unittest.TextTestRunner(verbosity=2).run(big_suite)