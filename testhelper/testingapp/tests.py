from testhelper.testcase import DjangoTestCase

from testhelper.testingapp import models

class TestHelperTests(DjangoTestCase):
    def setUp(self):
        self.test_models = [
            models.Category,
            models.Article,
            models.Tag,
        ]
        self.initial_defaults = {}
        self._store_initial_defaults()

    def tearDown(self):
        self._restore_initial_defaults()

    def _restore_initial_defaults(self):
        for model in self.test_models:
            if self.initial_defaults[model]:
                model.Testing = self.initial_defaults[model]
            else:
                if hasattr(model, "Testing"):
                    del model.Testing

    def _store_initial_defaults(self):
        for model in self.test_models:
            if hasattr(model, "Testing"):
                self.initial_defaults[model] = model.Testing
            else:
                self.initial_defaults[model] = None

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

        c = self.create_object(models.Category)

        post_save_defaults = { 'category': c }
        a = self.create_object(models.Article)
        self.assertEqual(a.category, c)
    
    def test_create_valid_object(self):
        """
        If a user has provided sufficient Testing.defaults and
        Testing.post_save_defaults to save their object,
        create_valid_object will return an instance of the object
        that has been saved into the database.
        """
        c = self.create_valid_object(models.Category)
        self.assert_(c.id)
        
        t = self.create_valid_object(models.Tag)
        self.assert_(c.id)

    def test_object_creation_with_overrides(self):
        """
        You should be able to pass overrides
        """
        pass