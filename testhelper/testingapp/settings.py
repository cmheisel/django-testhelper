from django.conf.global_settings import *

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = ':memory:'

ROOT_URLCONF = 'testhelper.testingapp.urls'

DEBUG = False
TEMPLATE_DEBUG = DEBUG

SITE_ID = 1

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.sessions',
    'django_nose',
    'testhelper.testingapp',
)

TEST_RUNNER = 'django_nose.run_tests'
