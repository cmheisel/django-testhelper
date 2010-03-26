from __future__ import with_statement
import datetime

from testhelper.testcase import DjangoTestCase
from testhelper.testingapp import models

class TestHelperTests(DjangoTestCase):
    def setUp (self):
        self.test_models = [
            models.Category,
            models.Article,
            models.Tag,
        ]
        self.initial_defaults = {}
        self._store_initial_defaults()
        super(TestHelperTests, self).setUp()

    def tearDown(self):
        self._restore_initial_defaults()
        super(TestHelperTests, self).tearDown()

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
        post_save_defaults = {
            'category': models.Category,
            'tags': models.Tag,
            'archive': models.Archive,
        }        
        models.Article.Testing.defaults = defaults
        models.Article.Testing.post_save_defaults = post_save_defaults

        a = self.create_object(models.Article)
        self.assert_(a.category)

        c = self.create_object(models.Category)

        post_save_defaults = { 'category': c }
        models.Article.Testing.post_save_defaults = post_save_defaults
        a = self.create_object(models.Article)
        self.assertEqual(a.category, c)

    def test_create_valid_object(self):
        """
        If a user has provided sufficient Testing.defaults and
        Testing.post_save_defaults to save their object,
        create_valid_object will return an instance of the object
        that has been saved into the database.
        """
        t = self.create_valid_object(models.Tag)
        self.assert_(t.id)

    def test_object_creation_with_overrides(self):
        """
        You should be able to pass overrides
        """
        overrides = {
            'name': 'I, Roommate',
            'boolean': True,
        }
        a = self.create_object(models.Article, overrides)
        self.assertEqual(a.name, overrides['name'])
        self.assertEqual(a.boolean, overrides['boolean'])
    
    def test_unique_object_id_creation(self):
        overrides = {
            'integer': '#{ran_i}',
        }
        results = []
        
        #seed the object_indexes tracker
        for i in xrange(0,1000):
            self.create_random_unique_integer()
        
        for i in xrange(0,3):
            a = self.create_object(models.Article, overrides)
            results.append(a.integer)
        self.assertEqual(len(results), len(set(results)), "All randomly created integers should be unique")

    def test_object_creation_expansion(self):
        """
        Values passed in as overrides and set as Testing.defaults should
        expand out special values for a random integer (as a string), a 
        random integer, and the current date time.
        """
        overrides = {
            'name': 'Space Pilot #{ran}',
            'integer': '#{ran_i}',
            'created_at': '#{now}',
        }
        a = self.create_object(models.Article, overrides)
        self.assertTrue("{ran}" not in a.name)
        self.assertEqual(type(a.integer), type(5))
        self.assertEqual(type(a.created_at), type(datetime.datetime.now()))
        
        models.Article.Testing.defaults = overrides
        a = self.create_valid_object(models.Article)
        self.assertTrue("{ran}" not in a.name)
        self.assertEqual(type(a.integer), type(5))
        self.assertEqual(type(a.created_at), type(datetime.datetime.now()))
        
    def test_get_template(self):
        """
            self.get_template should return the 0th (default) or nth template
            when an index argument is provided.
        """
        
        r = self.client.get('/multi-template/')
        self.assertEqual('testingapp/multi-template.html', self.get_template(r).name)
        self.assertEqual('testingapp/base.html', self.get_template(r, 1).name)
        
        r = self.client.get('/single-template/')
        self.assertEqual('testingapp/single-template.html', self.get_template(r).name)
    
    def test_unittest2_inheritance(self):
        """
            The methods and behavior of unittest2.TestCase should be a part of 
            any sublcass of testhelper.testcase.DjangoTestCase
        """
        self.assertIn("foo", "food")
        self.assertNotIn("bar", "foo")
    
    def test_assert404(self):
        """
            assert404 should pass on 404ing URLs and fail on non-404s.
        """
        r = self.client.get('/does-not-exist/')
        self.assert404(r)
        
        r = self.client.get('/single-template/')
        
        with self.assertRaises(AssertionError):
            self.assert404(r)

    def test_assert200(self):
        """
            assert200 should pass on 200ing URLs and fail on non-200s
        """
        r = self.client.get('/does-not-exist/')
        with self.assertRaises(AssertionError):
            self.assert200(r)
            
        r = self.client.get('/single-template') #should redirect
        with self.assertRaises(AssertionError):
            self.assert200(r)

        r = self.client.get('/single-template/')
        self.assert200(r)

    def test_close_datetimes(self):
        """
            Should pass for datetimes that almost equal, but fail on ones
            that aren't.
        """
        d1 = datetime.datetime.now()
        d2 = d1 + datetime.timedelta(seconds=2)
        self.assertCloseDatetimes(d1, d2)
    
    def test_assertContentType(self):
        """
            Should pass if the content types match
        """
        r = self.client.get('/single-template/')
        print r["Content-Type"]
        self.assertContentType(r, 'text')
        self.assertContentType(r, 'text/html')
        
        with self.assertRaises(AssertionError):
            self.assertContentType(r, 'text/xml')