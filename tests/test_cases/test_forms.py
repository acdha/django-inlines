from django import forms

from django_inlines import registry
from django_inlines.forms import InlineField

from test_app.inlines import BasicInline

from .test_common import InlinesTestCase

__all__ = ('InlineFormTestCase',)


class InlineForm(forms.Form):
    content = InlineField()


class InlineFormTestCase(InlinesTestCase):

    def setUp(self):
        registry.register('echo', BasicInline)

    def test_valid_form(self):
        form = InlineForm({
            'content':
            u'{{ echo arg1 arg2 kwarg1=kwarg1 kwarg2=kwarg2 }}'})

        self.assertTrue(form.is_valid())

    def test_syntax_errors(self):
        content = u'''
            {{ }}

            Text Token

            {{ echo2 }}

            {{ echo arg1=arg1 arg2 kwarg1=kwarg1 kwarg2=kwarg2 }}
        '''

        form = InlineForm({'content': content})

        self.assertFalse(form.is_valid())
        self.assertEqual([
            u'Syntax error on line 2. Empty inline found.',
            u'Syntax error on line 6. Inline `echo2` is not registered.',
            u'Syntax error on line 8. Inline `echo arg1=arg1 arg2 '
            u'kwarg1=kwarg1 kwarg2=kwarg2`, non-keyword argument found '
            u'after keyword argument.'],
            form.errors['content'])

    def test_inline_errors(self):
        content = u'''{{ echo arg1 arg3 kwarg1=kwarg1 kwarg2=kwarg2 }}
        '''

        form = InlineForm({'content': content})

        self.assertFalse(form.is_valid())
        self.assertEqual([
            u'Inline error on line 1. Inline `echo arg1 arg3 kwarg1=kwarg1 '
            u'kwarg2=kwarg2`, argument `arg2` (pos 2): `arg3` is not a valid '
            u'choice.'],
            form.errors['content'])

    def test_inline_and_syntax_errors(self):
        content = u'''
            {{ }}

            Text Token

            {{ echo2 }}
            {{ echo arg1 arg3 kwarg1=kwarg1 kwarg2=kwarg2 }}
            {{ echo arg1=arg1 arg2 kwarg1=kwarg1 kwarg2=kwarg2 }}
        '''

        form = InlineForm({'content': content})

        self.assertFalse(form.is_valid())

        self.assertEqual([
            u'Syntax error on line 2. Empty inline found.',
            u'Syntax error on line 6. Inline `echo2` is not registered.',
            u'Inline error on line 7. Inline `echo arg1 arg3 kwarg1=kwarg1 '
            u'kwarg2=kwarg2`, argument `arg2` (pos 2): `arg3` is not a valid '
            u'choice.',
            u'Syntax error on line 8. Inline `echo arg1=arg1 arg2 '
            u'kwarg1=kwarg1 kwarg2=kwarg2`, non-keyword argument found '
            u'after keyword argument.', ],
            form.errors['content'])
