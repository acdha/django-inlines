try:
    # Python 2
    from itertools import izip_longest as zip_longest
except ImportError:
    # Python 3
    from itertools import zip_longest

from django.core.exceptions import ValidationError

from django_inlines import registry, renderer

from test_app.inlines import BasicInline, BasicInlineParent

from .test_common import InlinesTestCase

__all__ = ('BasicInlineTestCase',)


class BasicInlineTestCase(InlinesTestCase):

    def setUp(self):
        registry.register('echo', BasicInline)

    def test_app_label(self):
        self.assertEqual('test_label', BasicInline._meta.app_label)

    def test_ordering(self):
        self.assertEqual(['arg1', 'arg2'], BasicInline._meta.ordering)
        self.assertEqual(['arg2', 'arg1'], BasicInlineParent._meta.ordering)

    def test_basic_inline_render(self):
        self.assertEqual(
            u'arg1 arg2 None kwarg2',
            renderer.render('{{ echo arg1 arg2 }}', raise_errors=True))

        self.assertEqual(
            u'arg1 arg2 kwarg1 kwarg2',
            renderer.render(
                '{{ echo arg1 \'arg2\' kwarg1="kwarg1" }}',
                raise_errors=True))

        self.assertEqual(
            u'arg1 arg2 kwarg1 hope',
            renderer.render(
                '{{ echo arg1 arg2 kwarg1=kwarg1 kwarg2=hope }}',
                raise_errors=True))

        self.assertEqual(
            u'arg1 arg2 kwarg1 kwarg2',
            renderer.render(
                '{{ echo arg1 arg2 kwarg2=kwarg2 kwarg1=kwarg1 }}',
                raise_errors=True))

    def test_unexpected_kwarg(self):
        self.assertRaisesMessage(
            ValidationError,
            u'Inline `echo arg1 arg2 kwarg4=kwarg4`:  Got an unexpected '
            u'keyword argument `kwarg4`',
            renderer.render, u'{{ echo arg1 arg2 kwarg4=kwarg4 }}',
            None, True)

    def test_arg_validation_error(self):
        self.assertRaisesMessage(
            ValidationError,
            u'Inline `echo arg1 arg3 kwarg2=kwarg2 kwarg1=kwarg1`, argument'
            u' `arg2` (pos 2): `arg3` is not a valid choice.',
            renderer.render,
            u'{{ echo arg1 arg3 kwarg2=kwarg2 kwarg1=kwarg1 }}',
            None, True)

    def test_variant(self):
        self.assertEqual(
            u'ARG1 ARG2 NONE KWARG2',
            renderer.render('{{ echo:upper arg1 arg2 }}', raise_errors=True))

        self.assertRaisesMessage(
            ValidationError,
            u'`downer` is not a valid variant for inline `echo`',
            renderer.render,
            u'{{ echo:downer arg1 arg2 kwarg2=kwarg2 kwarg1=kwarg1 }}',
            None, True)
