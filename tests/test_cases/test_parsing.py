from django.test import TestCase

from django_inlines import registry
from django_inlines.parsing import Lexer, Parser
from django_inlines.errors import InlineSyntaxError

from test_app.inlines import *

from .test_common import InlinesTestCase

__all__ = ('LexerTestCase', 'ParserTestCase',)


class LexerTestCase(TestCase):

    def test_lexer(self):
        tokens = Lexer('No inlines').tokenize()

        self.assertEqual(1, len(tokens))

        token = tokens[0]

        self.assertEqual('No inlines', token.contents)

        tokens = Lexer(
            '{{ test }} {{ test arg kwarg=1 }}').tokenize()

        self.assertEqual(3, len(tokens))

        t1, t2, t3 = tokens

        self.assertEqual('test', t1.contents)
        self.assertEqual(' ', t2.contents)
        self.assertEqual('test arg kwarg=1', t3.contents)

        tokens = Lexer(
            '{{ test }} space\n{{ test arg1 }}').tokenize()

        t1, t2, t3 = tokens

        self.assertEqual(1, t1.lineno)
        self.assertEqual(1, t2.lineno)
        self.assertEqual(2, t3.lineno)


class ParserTestCase(InlinesTestCase):

    def setUp(self):
        registry.register('echo', BasicInline)

    def test_parser(self):
        _, errors = Parser().parse('{{ echo hi }}')

        self.assertFalse(bool(errors))

    def test_syntax_errors(self):
        _, errors = Parser().parse('{{ }}')

        self.assertEqual(1, len(errors))
        self.assertIsInstance(errors[0], InlineSyntaxError)
        self.assertEqual(
            u'Empty inline found.', errors[0].messages[0])

        _, errors = Parser().parse('{{ echo2 }}')

        self.assertEqual(1, len(errors))
        self.assertIsInstance(errors[0], InlineSyntaxError)

        self.assertEqual(
            u'Inline `echo2` is not registered.', errors[0].messages[0])

        _, errors = Parser().parse('{{ echo kwarg1=1 arg1 }}')

        self.assertEqual(1, len(errors))
        self.assertIsInstance(errors[0], InlineSyntaxError)
        self.assertEqual(
            u'Inline `echo kwarg1=1 arg1`, non-keyword argument found after '
            u'keyword argument.', errors[0].messages[0])

        _, errors = Parser().parse(
            '{{ }}{{ echo2 }}{{ echo kwarg1=1 arg1 }}')

        self.assertEqual(3, len(errors))
