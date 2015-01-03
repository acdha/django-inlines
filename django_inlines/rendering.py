import logging
from itertools import chain

from django.conf import settings

from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

from django.core.exceptions import ValidationError

from .parsing import Parser
from .errors import InlineValidationError, create_verbose_inline_errors

__all__ = ('Renderer', 'renderer',)


logger = logging.getLogger(__name__)


class Renderer(object):

    def render(self, content, media=None,
               raise_errors=False, log_errors=False, verbose_errors=True):
        try:
            nodes, syntax_errors = Parser(media=media).parse(content)
            content, inline_errors = self.render_nodes(nodes, media)
        except Exception as err:
            if log_errors:
                logger.exception(err)
            if getattr(settings, 'INLINE_DEBUG', raise_errors):
                raise
            return u''

        if bool(syntax_errors or inline_errors):
            errors = [
                ve[1] for ve in sorted(
                    chain(
                        ((se.lineno, se) for se in syntax_errors),
                        ((ie.lineno, ie) for ie in inline_errors)),
                    key=lambda obj: obj[0])]

            validation_errors = \
                create_verbose_inline_errors(errors) \
                if verbose_errors else ValidationError(errors)

            if log_errors:
                for error_msg in validation_errors.messages:
                    logger.error(error_msg)
            if raise_errors:
                raise validation_errors
            return u''
        return mark_safe(content)

    def render_nodes(self, nodes, media):
        bits = []
        errors = []
        for node in nodes:
            try:
                bit = node.render(media)
            except ValidationError as err:
                bit = u''
                errors.extend(
                    (InlineValidationError(node.lineno, msg)
                        for msg in err.messages))
            bits.append(force_text(bit))
        return u''.join(bits), errors


renderer = Renderer()
