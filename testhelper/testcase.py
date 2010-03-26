from urlparse import urlparse
import unittest, random, datetime, pprint

from django.test import TestCase
from django.test.client import Client
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.db import models

TIMESTAMPING_CHECKED = False

def run_if_mysql(orig_function):
    '''Runs the test only if MySQL is the database engine in settings.DATABASE_ENGINE'''
    def _test_always_passes(*args, **kwargs):
        #print "Not running the test %s because database engine isn't MySQL" % (orig_function.__name__)
        assert(True)
    
    from django.conf import settings
    if settings.DATABASE_ENGINE != "mysql":
        return _test_always_passes
    else: # pragma: no cover
        return orig_function

class DjangoTestCase(TestCase):
    object_indexes = []

    def setUp(self):
        self.admin_user_password = "admin_password"
        self.admin_user = User(username="admin_username", email='admin_username@fake.com', is_staff=True, is_active=True, is_superuser=True)
        self.admin_user.set_password(self.admin_user_password)
        self.admin_user.save()
        self.assertValidObject(self.admin_user)

    def create_object(self, klass, overrides = dict()):
        if hasattr(klass, 'Testing') and hasattr(klass.Testing, 'defaults'):
            initial_values = klass.Testing.defaults.copy()
        else:
            initial_values = {}

        if overrides:
            initial_values.update(overrides)

        self.obj_index = self.create_object_index()
        for key, value in initial_values.items():
            initial_values[key] = self.__expand_default_value(value)

        o = klass(**initial_values)

        try:
            post_save_defaults = klass.Testing.post_save_defaults.copy()
            o.save()
            for key, value in post_save_defaults.items():
                value = self.__expand_default_value(value)
                try:
                    setattr(o, key, value)
                except TypeError:
                    setattr(o, key, [value, ])
            o.save()
        except AttributeError:
            pass #Doesn't have any post_save defaults

        return o

    def __expand_default_value(self, value):
        "Inserts random numbers, ints, or instantiates classes."
        obj_index = self.obj_index
        if hasattr(value, "startswith") and "#{ran}" in value:
            value = value.replace("#{ran}", str(obj_index))
        elif hasattr(value, "startswith") and "#{ran_i}" in value:
            value = int(value.replace("#{ran_i}", str(obj_index)))
        elif hasattr(value, "startswith") and "#{now}" in value:
            value = datetime.datetime.now()
        try:
            #Maybe you passed in a class
            value = self.create_valid_object(value)
        except TypeError:
            pass
            
        return value

    def create_valid_object(self, klass):
        o = self.create_object(klass)
        o.save()
        
        self.assert_(o.id, "We should have a valid saved object")
        return o

    def create_object_index(self):
        return self.create_random_unique_integer()

    def create_random_unique_integer(self, max_value=99999):
        """
            Returns a random, but unique integer.
            Uniqeness is per instance of DjangoTestCase, as 'used' integers
            are stored in an instance's object_indexes array.
        """
        random_int = self.create_random_integer(max_value)
        while random_int in self.object_indexes:
            #We've got a duplicate here, try again
            random_int = self.create_random_integer(max_value=max_value+1)

        self.object_indexes.append(random_int)
        return random_int

    def create_random_integer(self, max_value=99999):
        return random.randint(1, max_value)

    def get_template(self, response, index=0):
        """
            Returns the first template from the response, or optionally pass 
            in an index to return the nth template.
            
            This is a consistent method for accessing the template name.
            Useful when a view uses template inheritance as response.template
            changes from the template file name, to an array of file names.
        """
        try:
            return response.template[index]
        except TypeError:
            return response.template

    def assertStringContains(self, test_string, content_string, msg = None, assert_not_contains = False):
        if not msg:
            msg = """'%s' not in '%s'""" % (test_string, content_string)
            if assert_not_contains:
                msg = """'%s' in '%s'""" % (test_string, content_string)

        if assert_not_contains:
            self.assert_(test_string not in content_string, msg)
        else:
            self.assert_(test_string in content_string, msg)

    def assertNotStringContains(self, test_string, content_string, msg = None):
        self.assertStringContains(test_string, content_string, msg, assert_not_contains = True)

    def assert404(self, response):
        self.assertEqual(response.status_code, 404, "We should have a 404 response: %s != %s" % (response.status_code, 404))

    def assertValidResponse(self, response):
        self.assertEqual(response.status_code, 200, "We should have a valid response: %s != %s" % (response.status_code, 200))

    def assertValidObject(self, instance):
        instance.save()
        self.assert_(instance.id, "Valid objects should be save()-able and have an id.")

    def assertContentType(self, response, content_type):
        self.assert_(response["Content-Type"].startswith(content_type), "%s does not start with %s" % (response["Content-Type"], content_type))

    def assertValidJson(self, content_string):
        import simplejson
        json_feed = simplejson.loads(content_string)
        if not json_feed: # pragma: no cover
            raise self.failureException, "This isn't valid JSON:\n%s" % (content_string)

    def assertCloseDateTimes(self, expected, actual):
        delta = expected - actual
        msg = "Expected datetime: %s is not within 5 seconds of the actual datetime: %s" % (expected, actual)
        self.assert_(delta.seconds <= 5, msg)