from testhelper.testcase import DjangoTestCase

from testhelper.testingapp import models

class TestHelperTests(DjangoTestCase):
    def test_object_creation_without_defaults(self):
        """
        Calling create_object should return an instance of the model even if 
        it doesn't have a Testing inner class with a defaults property.
        """
        t = self.create_object(models.Tag)
        self.assert_(isinstance(t, models.Tag))

        c = self.create_object(models.Category)
        self.assert_(isinstance(c, models.Category))

    def test_object_creation_with_defaults(self):
        """
        If an object contains an inner class Testing with defaults property
        then the instance returned should use that default.
        """
        defaults = { 'name': 'Space Pilot 3000' }
        models.Article.Testing.defaults = defaults

        a = self.create_object(models.Article)
        self.assertEqual(defaults['name'], a.name)

    def test_object_creation_with_default_relations(self):
        """
        Default relations should be able to be specified
        """
        defaults = { 'name': 'Space Pilot 3000' }
        post_save_defaults = { 'category': models.Category }
        models.Article.Testing.defaults = defaults
        models.Article.Testing.post_save_defaults = post_save_defaults
        
        a = self.create_object(models.Article)
        self.assert_(a.category)
        