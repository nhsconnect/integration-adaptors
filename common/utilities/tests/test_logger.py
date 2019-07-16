from unittest import TestCase

from common.utilities import logger


class TestLogger(TestCase):

    def test_thing(self):
        logger.Logger("", log_level=0)\
            .audit('{There Will Be No Spaces Today}', {'There Will Be No Spaces Today': 'wow qwe'}, correlation_id=2)
