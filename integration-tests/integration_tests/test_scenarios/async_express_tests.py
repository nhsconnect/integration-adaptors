from unittest import skip, TestCase

from integration_tests.helpers import methods, interactions


class FunctionalTest(TestCase):

    skip('duplicate')
    def test_mhs_async_express(self):
        mhs_response = methods.get_interaction_from_template('QUPC_IN160101UK05',
                                                             '9689174746',
                                                             'Asynchronous Express test')
        self.assertTrue(methods.check_response(mhs_response), "Asynchronous Express test failed")
