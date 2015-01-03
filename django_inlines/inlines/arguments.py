import re

from decimal import Decimal, DecimalException

from django.core.exceptions import ValidationError
from django.core import validators as core_validators

from django.utils import six
from django.utils.encoding import force_text, smart_text
from django.utils.translation import ugettext_lazy as _, ungettext_lazy as _n

__all__ = (
    'Argument', 'BooleanArgument', 'NullBooleanArgument', 'CharArgument',
    'EmailArgument', 'IntegerArgument', 'RegexArgument', 'SlugArgument',
    'URLArgument', 'DecimalArgument', 'FloatArgument',)


class Argument(object):
    creation_counter = 0
    default_validators = []
    default_error_messages = {
        'invalid_choice': _(u'`%(value)s` is not a valid choice.'), }
    empty_values = list(core_validators.EMPTY_VALUES)

    def __init__(self, choices=None, validators=None, error_messages=None,
                 keyword=False, default=None, help_text=None):
        self.name = None
        self.choices = choices
        self.default = default
        self.keyword = keyword
        self.help_text = help_text

        if validators is not None:
            self.validators = self.default_validators + validators
        else:
            self.validators = list(self.default_validators)

        self.creation_counter = Argument.creation_counter
        Argument.creation_counter += 1

        messages = {}

        for c in reversed(self.__class__.__mro__):
            messages.update(getattr(c, 'default_error_messages', {}))

        if error_messages:
            messages.update(error_messages)

        self.error_messages = messages

    def is_valid_choice(self, value):
        if self.choices is None:
            return True
        else:
            text_value = force_text(value)
            for k, v in self.choices:
                if value == k or text_value == force_text(k):
                    return True
            return False

    def validate(self, value):
        errors = []

        if not self.is_valid_choice(value):
            errors.append(
                ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice', params={'value': value}))

        for validator in self.validators:
            try:
                validator(value)
            except ValidationError as e:
                if hasattr(e, 'code') and e.code in self.error_messages:
                    e.message = self.error_messages[e.code]
                errors.extend((ValidationError(msg) for msg in e.messages))

        if errors:
            raise ValidationError(errors)

    def to_python(self, value):
        return value

    def process(self, value):
        value = self.to_python(value)
        self.validate(value)
        return value


class BooleanArgument(Argument):

    def to_python(self, value):
        if isinstance(value, six.string_types) and \
                value.lower() in ('false', '0',):
            value = False
        else:
            value = bool(value)
        return value


class NullBooleanArgument(BooleanArgument):

    def to_python(self, value):
        if value is not None:
            value = value.lower()
            if value in (True, 'true', '1'):
                return True
            elif value in (False, 'false', '0'):
                return False
        return None


class CharArgument(Argument):

    def __init__(self, max_length=None, min_length=None, *args, **kwargs):
        super(CharArgument, self).__init__(*args, **kwargs)
        self.max_length, self.min_length = max_length, min_length

        if min_length is not None:
            self.validators.append(
                core_validators.MinLengthValidator(int(min_length)))

        if max_length is not None:
            self.validators.append(
                core_validators.MaxLengthValidator(int(max_length)))

    def to_python(self, value):
        if value in self.empty_values:
            return ''

        return smart_text(value)


class EmailArgument(CharArgument):
    default_validators = [core_validators.validate_email]


class IntegerArgument(Argument):
    default_error_messages = {'invalid': _('Enter a whole number.')}

    def __init__(self, max_value=None, min_value=None, *args, **kwargs):
        self.max_value, self.min_value = max_value, min_value
        super(IntegerArgument, self).__init__(*args, **kwargs)

        if max_value is not None:
            self.validators.append(
                core_validators.MaxValueValidator(max_value))
        if min_value is not None:
            self.validators.append(
                core_validators.MinValueValidator(min_value))

    def to_python(self, value):
        if value in self.empty_values:
            return None

        try:
            value = int(str(value))
        except (ValueError, TypeError):
            raise ValidationError(
                self.error_messages['invalid'], code='invalid')

        return value


class RegexArgument(CharArgument):

    def __init__(self, regex, *args, **kwargs):
        super(RegexArgument, self).__init__(*args, **kwargs)
        self.set_regex(regex)

    def set_regex(self, regex):
        if isinstance(regex, six.string_types):
            regex = re.compile(regex, re.UNICODE)
        self._regex = regex

        if hasattr(self, '_regex_validator') and \
                self._regex_validator in self.validators:
            self.validators.remove(self._regex_validator)
        self._regex_validator = core_validators.RegexValidator(regex=regex)
        self.validators.append(self._regex_validator)


class SlugArgument(CharArgument):
    default_validators = [core_validators.validate_slug]


class URLArgument(CharArgument):
    default_error_messages = {
        'invalid': _('Enter a valid URL.')}
    default_validators = [core_validators.URLValidator()]


class FloatArgument(IntegerArgument):
    default_error_messages = {
        'invalid': _('Enter a number.')}

    def to_python(self, value):
        if value in self.empty_values:
            return None

        try:
            value = float(value)
        except (ValueError, TypeError):
            raise ValidationError(
                self.error_messages['invalid'], code='invalid')

        return value

    def validate(self, value):
        super(FloatArgument, self).validate(value)

        if value != value or value in (Decimal('Inf'), Decimal('-Inf')):
            raise ValidationError(
                self.error_messages['invalid'], code='invalid')

        return value


class DecimalArgument(IntegerArgument):
    default_error_messages = {
        'invalid': _('Enter a number.'),
        'max_digits': _n(
            'Ensure that there are no more than %(max)s digit in total.',
            'Ensure that there are no more than %(max)s digits in total.',
            'max'),
        'max_decimal_places': _n(
            'Ensure that there are no more than %(max)s decimal place.',
            'Ensure that there are no more than %(max)s decimal places.',
            'max'),
        'max_whole_digits': _n(
            'Ensure that there are no more than %(max)s digit before the '
            'decimal point.',
            'Ensure that there are no more than %(max)s digits before the '
            'decimal point.',
            'max')}

    def __init__(self, max_value=None, min_value=None, max_digits=None,
                 decimal_places=None, *args, **kwargs):
        self.max_digits, self.decimal_places = max_digits, decimal_places
        super(DecimalArgument, self).__init__(
            max_value, min_value, *args, **kwargs)

    def to_python(self, value):
        if value in self.empty_values:
            return None

        value = smart_text(value).strip()

        try:
            value = Decimal(value)
        except DecimalException:
            raise ValidationError(
                self.error_messages['invalid'], code='invalid')

        return value

    def validate(self, value):
        super(DecimalArgument, self).validate(value)

        if value in self.empty_values:
            return

        if value != value or value == Decimal("Inf") \
                or value == Decimal("-Inf"):
            raise ValidationError(
                self.error_messages['invalid'], code='invalid')

        sign, digittuple, exponent = value.as_tuple()

        decimals = abs(exponent)
        digits = len(digittuple)

        if decimals > digits:
            digits = decimals

        whole_digits = digits - decimals

        if self.max_digits is not None and digits > self.max_digits:
            raise ValidationError(
                self.error_messages['max_digits'],
                code='max_digits',
                params={'max': self.max_digits})
        if self.decimal_places is not None and decimals > self.decimal_places:
            raise ValidationError(
                self.error_messages['max_decimal_places'],
                code='max_decimal_places',
                params={'max': self.decimal_places})
        if (self.max_digits is not None and self.decimal_places is not None
                and whole_digits > (self.max_digits - self.decimal_places)):
            raise ValidationError(
                self.error_messages['max_whole_digits'],
                code='max_whole_digits',
                params={'max': (self.max_digits - self.decimal_places)})

        return value
