from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import validate_integer
from django.utils.translation import ugettext_lazy as _

from django_inlines import inlines

from .test_common import InlinesTestCase

__all__ = ('ArgumentsTestCase',)


class ArgumentsTestCase(InlinesTestCase):

    def test_argument(self):
        arg = inlines.Argument()
        self.assertEqual('1', arg.process('1'))
        self.assertEqual('', arg.process(''))

    def test_argument_is_keyword(self):
        arg = inlines.Argument()
        self.assertFalse(arg.keyword)

        arg = inlines.Argument(keyword=True)
        self.assertTrue(arg.keyword)

    def test_default(self):
        arg = inlines.Argument()
        self.assertIsNone(arg.default)

        arg = inlines.Argument(default=1)
        self.assertEqual(1, arg.default)

    def test_argument_choices(self):
        CHOICE_1 = u'1'
        CHOICE_2 = u'2'

        CHOICES = (
            (CHOICE_1, _(u'1'),),
            (CHOICE_2, _(u'2'),),)

        arg = inlines.Argument(choices=CHOICES)

        self.assertRaisesMessage(
            ValidationError, u'`3` is not a valid choice.', arg.process, '3')

        arg = inlines.Argument(
            choices=CHOICES, error_messages={
                'invalid_choice':
                u'`%(value)s`! `%(value)s`!? '
                u'You\'re not looking at the big picture!! `%(value)s`'})

        self.assertRaisesMessage(
            ValidationError,
            u'`3`! `3`!? You\'re not looking at the big picture!! `3`',
            arg.process, '3')

    def test_argument_validators(self):
        arg = inlines.Argument(
            validators=[validate_integer],
            error_messages={'invalid':  u'Nope'})
        self.assertRaisesMessage(ValidationError, u'Nope', arg.process, 'e')

    def test_int_argument(self):
        arg = inlines.IntegerArgument()
        self.assertIsNone(arg.process(''))

        arg = inlines.IntegerArgument(min_value=1, max_value=10)

        self.assertEqual(1, arg.min_value)
        self.assertEqual(10, arg.max_value)

        self.assertEqual(3, arg.process('3'))
        self.assertRaisesMessage(
            ValidationError, u'Enter a whole number.', arg.process, 'e')

        self.assertRaisesMessage(
            ValidationError,
            u'Ensure this value is greater than or equal to 1.',
            arg.process, '0')

        self.assertRaisesMessage(
            ValidationError,
            u'Ensure this value is less than or equal to 10.',
            arg.process, '11')

        self.assertEqual(5, arg.process('5'))

    def test_bool_argument(self):
        arg = inlines.BooleanArgument()

        self.assertTrue(arg.process('1'))
        self.assertTrue(arg.process('a'))
        self.assertTrue(arg.process('True'))
        self.assertTrue(arg.process('tRue'))

        self.assertFalse(arg.process(''))
        self.assertFalse(arg.process('0'))
        self.assertFalse(arg.process('False'))
        self.assertFalse(arg.process('fAlse'))

    def test_null_bool_argument(self):
        arg = inlines.NullBooleanArgument()

        self.assertTrue(arg.process('1'))
        self.assertTrue(arg.process('True'))
        self.assertTrue(arg.process('tRue'))

        self.assertFalse(arg.process('0'))
        self.assertFalse(arg.process('False'))
        self.assertFalse(arg.process('fAlse'))

        self.assertIsNone(arg.process(''))
        self.assertIsNone(arg.process('a'))
        self.assertIsNone(arg.process('None'))
        self.assertIsNone(arg.process('noNe'))

    def test_email_argument(self):
        arg = inlines.EmailArgument()

        self.assertEqual(u'x@x.com', arg.process(u'x@x.com'))

        self.assertRaisesMessage(
            ValidationError, u'Enter a valid email address.',
            arg.process, 'x(a)x.com')

    def test_url_argument(self):
        arg = inlines.URLArgument()

        self.assertEqual(
            u'http://www.example.com/',
            arg.process(u'http://www.example.com/'))

        self.assertRaisesMessage(
            ValidationError, u'Enter a valid URL.', arg.process,
            'http//www.example.com/')

    def test_slug_argument(self):
        arg = inlines.SlugArgument()

        self.assertEqual(
            u'slug_slug_slug',
            arg.process(u'slug_slug_slug'))

        self.assertRaisesMessage(
            ValidationError,
            u'Enter a valid \'slug\' consisting of letters, numbers, '
            u'underscores or hyphens.', arg.process,
            'slug slug slug')

    def test_regex_argument(self):
        arg = inlines.RegexArgument(r'(\d+)')

        self.assertEqual(u'5', arg.process(u'5'))

        self.assertRaisesMessage(
            ValidationError, u'Enter a valid value.', arg.process, 'a')

        arg.set_regex(r'(\w+)')

        self.assertEqual(u'a', arg.process(u'a'))

    def test_char_argument(self):
        arg = inlines.CharArgument()

        self.assertEqual(u'1', arg.process(1))
        self.assertEqual(u'', arg.process(None))
        self.assertEqual(u'', arg.process(None))

        arg = inlines.CharArgument(min_length=10)

        self.assertRaisesMessage(
            ValidationError,
            u'Ensure this value has at least 10 characters (it has 4).',
            arg.process, 'Test')

        arg = inlines.CharArgument(max_length=1)

        self.assertRaisesMessage(
            ValidationError,
            u'Ensure this value has at most 1 character (it has 4).',
            arg.process, 'Test')

    def test_decimal_argument(self):
        arg = inlines.DecimalArgument(max_digits=4, decimal_places=2)

        self.assertIsNone(arg.process(''))
        self.assertEqual(arg.process('1'), Decimal("1"))
        self.assertEqual(True, isinstance(arg.process('1'), Decimal))
        self.assertEqual(arg.process('23'), Decimal("23"))
        self.assertEqual(arg.process('3.14'), Decimal("3.14"))
        self.assertEqual(arg.process(3.14), Decimal("3.14"))
        self.assertEqual(arg.process(Decimal('3.14')), Decimal("3.14"))
        self.assertRaisesMessage(
            ValidationError, "'Enter a number.'", arg.process, 'NaN')
        self.assertRaisesMessage(
            ValidationError, "'Enter a number.'", arg.process, 'Inf')
        self.assertRaisesMessage(
            ValidationError, "'Enter a number.'", arg.process, '-Inf')
        self.assertRaisesMessage(
            ValidationError, "'Enter a number.'", arg.process, 'a')
        self.assertEqual(arg.process('1.0 '), Decimal("1.0"))
        self.assertEqual(arg.process(' 1.0'), Decimal("1.0"))
        self.assertEqual(arg.process(' 1.0 '), Decimal("1.0"))
        self.assertRaisesMessage(
            ValidationError, "'Enter a number.'", arg.process, '1.0a')
        self.assertRaisesMessage(
            ValidationError,
            "'Ensure that there are no more than 4 digits in total.'",
            arg.process, '123.45')
        self.assertRaisesMessage(
            ValidationError,
            "'Ensure that there are no more than 2 decimal places.'",
            arg.process, '1.234')
        self.assertRaisesMessage(
            ValidationError,
            "'Ensure that there are no more than 2 digits before the decimal "
            "point.'", arg.process, '123.4')
        self.assertEqual(arg.process('-12.34'), Decimal("-12.34"))
        self.assertRaisesMessage(
            ValidationError, "'Ensure that there are no more than 4 digits in "
            "total.'", arg.process, '-123.45')
        self.assertEqual(arg.process('-.12'), Decimal("-0.12"))
        self.assertEqual(arg.process('-00.12'), Decimal("-0.12"))
        self.assertEqual(arg.process('-000.12'), Decimal("-0.12"))
        self.assertRaisesMessage(
            ValidationError, "'Ensure that there are no more than 2 decimal "
            "places.'", arg.process, '-000.123')
        self.assertRaisesMessage(
            ValidationError, "'Ensure that there are no more than 4 digits in "
            "total.'", arg.process, '-000.12345')
        self.assertRaisesMessage(
            ValidationError, "'Enter a number.'", arg.process, '--0.12')
        self.assertEqual(arg.max_digits, 4)
        self.assertEqual(arg.decimal_places, 2)
        self.assertEqual(arg.max_value, None)
        self.assertEqual(arg.min_value, None)

    def test_float_argument(self):
        arg = inlines.FloatArgument()

        self.assertIsNone(arg.process(''))
        self.assertEqual(1.0, arg.process('1'))
        self.assertEqual(True, isinstance(arg.process('1'), float))
        self.assertEqual(23.0, arg.process('23'))
        self.assertEqual(3.1400000000000001, arg.process('3.14'))
        self.assertEqual(3.1400000000000001, arg.process(3.14))
        self.assertEqual(42.0, arg.process(42))
        self.assertRaisesMessage(
            ValidationError, "'Enter a number.'", arg.process, 'a')
        self.assertEqual(1.0, arg.process('1.0 '))
        self.assertEqual(1.0, arg.process(' 1.0'))
        self.assertEqual(1.0, arg.process(' 1.0 '))
        self.assertRaisesMessage(
            ValidationError, "'Enter a number.'", arg.process, '1.0a')
        self.assertEqual(arg.max_value, None)
        self.assertEqual(arg.min_value, None)
        self.assertRaisesMessage(
            ValidationError, "'Enter a number.'", arg.process, 'Infinity')
        self.assertRaisesMessage(
            ValidationError, "'Enter a number.'", arg.process, 'NaN')
        self.assertRaisesMessage(
            ValidationError, "'Enter a number.'", arg.process, '-Inf')
