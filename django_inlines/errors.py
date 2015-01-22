from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

__all__ = (
    'InlineValidationError', 'InlineSyntaxError',
    'create_verbose_inline_errors',)


class InlineValidationError(ValidationError):

    def __init__(self, lineno, *args, **kwargs):
        self.lineno = lineno
        super(InlineValidationError, self).__init__(*args, **kwargs)


class InlineSyntaxError(InlineValidationError):
    pass


def create_verbose_inline_errors(err):
    errors = []
    error_list = err.error_list if isinstance(err, ValidationError) else err
    for error in error_list:
        if isinstance(error, InlineSyntaxError):
            error_class = InlineSyntaxError
            msg_template = _(u'Syntax error on line %(lineno)d. %(message)s')
        elif isinstance(error, InlineValidationError):
            error_class = InlineValidationError
            msg_template = _(u'Inline error on line %(lineno)d. %(message)s')

        for msg in error.messages:
            error = error_class(
                error.lineno,
                msg_template,
                params={'lineno': error.lineno, 'message': msg})
            errors.append(error)

    return ValidationError(errors)
