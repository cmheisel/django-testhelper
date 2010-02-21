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

    def check_timestamping(self, klass, run_only_once=True):
        if run_only_once and testhelper.testcase.TIMESTAMPING_CHECKED:
            #We don't need to check every single time, once is enough if you're using testhelper.testcase.update_timestamps
            return True
            
        r = self.create_object(klass)

        now = datetime.datetime.now()
        r.save()

        for key in ["year", "month", "day", "hour", "minute", "second"]:
            now_value = getattr(now, key)
            created_at_value = getattr(r.created_at, key)
            updated_at_value = getattr(r.updated_at, key)

            self.assert_(now_value == created_at_value, """The object's created_at %s (%s) != the now value (%s)""" % (key, created_at_value, now_value) )
            self.assert_(now_value == updated_at_value, """The object's updated_at %s (%s) != the now value (%s)""" % (key, updated_at_value, now_value) )

        import time
        time.sleep(1.2)

        old_now = now
        now = datetime.datetime.now()
        
        r.save()
        for key in ["year", "month", "day", "hour", "minute", "second"]:
            now_value = getattr(now, key)
            old_now_value = getattr(old_now, key)
            created_at_value = getattr(r.created_at, key)
            updated_at_value = getattr(r.updated_at, key)

            self.assert_(old_now_value == created_at_value, "The object's created_at %s (%s) != the now value (%s)" % (key, created_at_value, now_value))
            self.assert_(now_value == updated_at_value, "The object's updated_at %s (%s) != the now value (%s)" % (key, updated_at_value, now_value))

        self.assertNotEqual(r.updated_at.second, r.created_at.second)

        testhelper.testcase.TIMESTAMPING_CHECKED = True
        return True

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
            value = self.create_object(value)
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
        random_int = self.create_random_integer(max_value)
        while random_int in self.object_indexes:
            #We've got a duplicate here, try again
            random_int = self.create_random_integer(max_value=max_value+1)

        self.object_indexes.append(random_int)
        return random_int

    def create_random_integer(self, max_value=99999):
        return random.randint(1, max_value)

    def cleanup_models(self, model_list):
        for model in model_list: model.objects.all().delete()

    def get_template(self, response, index=0):
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

    def check_object_list_view(self, app_url, expected_object_list, object_list_name, template_name, content_type):
        """Abstracted test function that checks app_url to make sure it uses template_name, returns content_type and has victim_list in the right order."""
        response = self.client.get(app_url)
        template = self.get_template(response, 0)

        self.assertValidResponse(response)

        actual = response.context[object_list_name]
        self.assertEqual(len(expected_object_list), actual.count())
        [ self.assertEqual(expected_object_list[i], actual[i]) for i in xrange(0,len(expected_object_list)) ]

        self.assertEqual(template.name, template_name)
        self.assertContentType(response, content_type)

    def check_draft_and_published_manager(self, klass):
        self.assertEqual(0, klass.draft_objects.count())

        o = self.create_object(klass, dict(status="Draft"))
        o.save()
        self.assertValidObject(o)
        self.assert_(o.status == "Draft")

        o2 = self.create_object(klass, dict(status="Published"))
        o2.save()
        self.assertValidObject(o2)
        self.assert_(o2.status == "Published")

        self.assertEqual(2, klass.objects.all().count())
        self.assertEqual(1, klass.draft_objects.count())
        self.assertEqual(1, klass.published_objects.count())

    def run(self, result=None):
        if result is None: result = self.defaultTestResult()
        try:
            super(DjangoTestCase, self).run(result)
        except KeyboardInterrupt: # pragma: no cover
            result.stop()

    def assertValidJson(self, content_string):
        import simplejson
        json_feed = simplejson.loads(content_string)
        if not json_feed: # pragma: no cover
            raise self.failureException, "This isn't valid JSON:\n%s" % (content_string)

    def assertCloseDateTimes(self, expected, actual):
        delta = expected - actual
        msg = "Expected datetime: %s is not within 5 seconds of the actual datetime: %s" % (expected, actual)
        self.assert_(delta.seconds <= 5, msg)

    def login_without_redirect(self, client, path, username, password, **extra):
        """
        A specialized sequence of GET and POST to log into a view that
        is protected by a @login_required access decorator.

        path should be the URL of the page that is login protected.

        Returns the response from GETting the requested URL after
        login is complete. Returns False if login process failed.
        """

        raise DeprecationWarning("This method doesn't appear to do anything.")
        form_data = {
            'username': username,
            'password': password,
            'this_is_the_login_form': '1',
        }
        response = client.post(path, data=form_data, **extra)