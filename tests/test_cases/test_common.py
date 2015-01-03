from django.test import TestCase

from django_inlines import registry

__all__ = ('InlinesTestCase',)


class InlinesTestCase(TestCase):

    def tearDown(self):
        super(InlinesTestCase, self).tearDown()
        registry.clear()
