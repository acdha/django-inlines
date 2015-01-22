try:
    # Python 2
    from itertools import izip_longest as zip_longest
except ImportError:
    # Python 3
    from itertools import zip_longest

try:
    from unittest.mock import patch
except ImportError:
    try:
        from mock import patch
    except ImportError:
        raise RuntimeError('Please install mock for testing on Python 2')

from django.core.exceptions import ValidationError

from django_inlines import registry, renderer

from test_app.inlines import (
    BasicInline, BasicMixInline, BasicInlineParent,)

from .test_common import InlinesTestCase

__all__ = ('RendererTestCase',)


class RendererTestCase(InlinesTestCase):

    def setUp(self):
        registry.register('echo', BasicInline)

    def test_validation_errors(self):
        # Test empty inline and `clean_arg1` validation errors
        with self.assertRaises(ValidationError) as cm:
            renderer.render(
                '{{ }}{{ echo hope arg2 kwarg2=kwarg2 }}',
                raise_errors=True, verbose_errors=False)

        self._test_validation_messages([
            u'Empty inline found.',
            u'Inline `echo hope arg2 kwarg2=kwarg2`, argument `arg1` (pos 1): '
            u'Validation Error 1',
            u'Inline `echo hope arg2 kwarg2=kwarg2`, argument `arg1` (pos 1): '
            u'Validation Error 2'], cm)

        # Test `clean` validation errors
        with self.assertRaises(ValidationError) as cm:
            renderer.render(
                '{{ echo \'a new\' "hope" }}',
                raise_errors=True, verbose_errors=False)

        self._test_validation_messages([
            u'Inline `echo \'a new\' "hope"`:  You are a part of the Rebel'
            u' Alliance and a traitor!'], cm)

        # Test inline w\ too few args
        with self.assertRaises(ValidationError) as cm:
            renderer.render(
                '{{ }}\n{{ echo 1 }}\n{{ }}',
                raise_errors=True, verbose_errors=False)

        self._test_validation_messages([
            u'Empty inline found.',
            u'Inline `echo 1`:  Takes at least 2 non-keyword arguments '
            u'(1 given).',
            u'Empty inline found.'], cm)

        # Test inline w\ too many args
        with self.assertRaises(ValidationError) as cm:
            renderer.render(
                '{{ echo a new hope }}',
                raise_errors=True, verbose_errors=False)

        self._test_validation_messages([
            u'Inline `echo a new hope`:  Takes only 2 non-keyword '
            u'arguments (3 given).'], cm)

        # Test arg found after kwarg
        with self.assertRaises(ValidationError) as cm:
            renderer.render(
                '{{ echo kw=1 \'a new\' "hope" }}',
                raise_errors=True, verbose_errors=False)

        self._test_validation_messages([
            u'Inline `echo kw=1 \'a new\' "hope"`, non-keyword argument '
            u'found after keyword argument.'], cm)

        # Test kwarg3 argument validator
        with self.assertRaises(ValidationError) as cm:
            renderer.render(
                '{{ echo arg1 arg2 kwarg3=rebel }}',
                raise_errors=True, verbose_errors=False)

        self._test_validation_messages([
            u'Inline `echo arg1 arg2 kwarg3=rebel`, argument `kwarg3`: '
            u'Enter a valid email address.',
            u'Inline `echo arg1 arg2 kwarg3=rebel`, argument `kwarg3`: Is a '
            u'part of the Rebel Alliance and a traitor!'], cm)

    def _test_validation_messages(self, expected, cm):
        for z in zip_longest(expected, cm.exception.messages):
            self.assertEqual(*z)

    def test_exceptions(self):
        registry.register('none', BasicInlineParent)
        self.assertEqual(u'', renderer.render('{{ echo }}', log_errors=False))
        self.assertEqual(u'', renderer.render('{{ none }}', log_errors=False))

    def test_exception_logging(self):
        with patch('django_inlines.rendering.logger.exception') as mock_log:
            self.assertEqual(u'', renderer.render('{{ echo:no-such-variant }}', log_errors=True))
            self.assertTrue(mock_log.called)

    def test_media(self):
        registry.unregister('echo')

        registry.register(
            'echo', BasicInline, media={'mix_mod_4': BasicMixInline})

        self.assertEqual(
            u'ArG1 aRg2 KwArG1 kWaRg2',
            renderer.render(
                u'{{ echo:mix arg1 arg2 kwarg1=kwarg1 kwarg2=kwarg2 }}'))

        self.assertEqual(
            u'Arg1 arg2 kwArg1 kwaRg2',
            renderer.render(
                u'{{ echo:mix arg1 arg2 kwarg1=kwarg1 kwarg2=kwarg2 }}',
                media='mix_mod_4'))
