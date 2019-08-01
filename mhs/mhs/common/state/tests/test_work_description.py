from unittest import TestCase

import mhs.common.state.work_description as wd


class TestWorkDescription(TestCase):

    def test_update(self):
        work = wd.WorkDescription()
        work.update()
