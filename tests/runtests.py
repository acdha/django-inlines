#!/usr/bin/env python

import os
import sys

import django

from django.conf import settings


sys.path.append(
    os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__))), '..'))


settings.configure(**{
    'INLINE_DEBUG': True,
    'MIDDLEWARE_CLASSES': (),
    'INSTALLED_APPS': ('django_inlines', 'test_app',),
    'DATABASES': {
        'default': {
            'NAME': 'sqlite.db',
            'ENGINE': 'django.db.backends.sqlite3'}}})


try:
    # Django 1.7
    django.setup()
except AttributeError:
    pass


from django.test.utils import get_runner


def main():
    test_runner = get_runner(settings)()
    failures = test_runner.run_tests(('test_cases',))

    if failures:
        sys.exit(bool(failures))


if __name__ == '__main__':
    main()
