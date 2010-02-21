from testhelper.testcase import DjangoTestCase

from testhelper.testingapp import models

class TestHelperTests(DjangoTestCase):
    def test_object_creation_without_defaults(self):
        """
        Calling create_object should return an instance of the model, with
        defaults pre-filled from class.Testing.defaults if available.
        """
        t = self.create_object(models.Tag)
        self.assertEqual('', t.name)

        c = self.create_object(models.Category)
        self.assertEqual('', c.name)

        