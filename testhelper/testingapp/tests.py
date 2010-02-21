from testhelper.testcase import DjangoTestCase

class TestHelperTests(DjangoTestCase):
    def test_truth(self):
        self.assert_(True)