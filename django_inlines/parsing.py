import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.text import smart_split, unescape_string_literal

from .registry import registry
from .errors import InlineSyntaxError, InlineValidationError

__all__ = ('Token', 'Lexer', 'BaseNode', 'InlineNode', 'TextNode', 'Parser',)


INLINE_START = getattr(settings, 'INLINE_TAG_START', '{{')
INLINE_END = getattr(settings, 'INLINE_TAG_END', '}}')

INLINE_START_LEN = len(INLINE_START)
INLINE_END_LEN = len(INLINE_END)

KWARG_RE = re.compile(r'(?:(\w+)=)?(.+)')
INLINE_RE = re.compile('(%s.*?%s)' % (
    re.escape(INLINE_START), re.escape(INLINE_END)))

TOKEN_TEXT = 0
TOKEN_INLINE = 1

TOKEN_MAPPING = {
    TOKEN_TEXT: 'Text',
    TOKEN_INLINE: 'Inline'}


class Token(object):

    def __init__(self, token_type, contents):
        self.lineno = None
        self.contents = contents
        self.token_type = token_type

    def __str__(self):
        return (
            '<%s token: "%s...">' % (
                TOKEN_MAPPING[self.token_type],
                self.contents.replace('\n', ''),))

    def split_contents(self):
        return list(smart_split(self.contents))


class Lexer(object):

    def __init__(self, content):
        self.lineno = 1
        self.content = content

    def tokenize(self):
        result = []
        in_tag = False

        for bit in INLINE_RE.split(self.content):
            if bit:
                result.append(self.create_token(bit, in_tag))
            in_tag = not in_tag

        return result

    def create_token(self, token_string, in_tag):
        if in_tag:
            if token_string.startswith(INLINE_START):
                token = Token(
                    TOKEN_INLINE,
                    token_string[INLINE_START_LEN:-INLINE_END_LEN].strip())
        else:
            token = Token(TOKEN_TEXT, token_string)

        token.lineno = self.lineno
        self.lineno += token_string.count('\n')

        return token


class BaseNode(object):

    def __init__(self, token):
        self.lineno = token.lineno
        self.contents = token.contents

    def render(self, variant):
        raise NotImplementedError


class InlineFactory(object):

    def __init__(self, inline_cls, name, args, kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.inline_cls = inline_cls

    def __call__(self):
        return self.inline_cls(self.name, *self.args, **self.kwargs)


class InlineNode(BaseNode):

    def __init__(self, inline_factory, variant, token):
        self.token = token
        self.variant = variant
        self.inline_factory = inline_factory
        super(InlineNode, self).__init__(token)

    def render(self, media=None):
        inline = self.inline_factory()

        if inline.is_valid():
            return inline.full_render(variant=self.variant, media=media)

        errors = []
        lineno = self.token.lineno

        for arg_name, arg_errors in inline.errors.items():
            arg_idx = inline.get_argument_index(arg_name)
            for validation_error in arg_errors:
                for message in validation_error.messages:
                    if arg_name is not None:
                        err = InlineValidationError(
                            lineno, _(
                                u'Inline `%(contents)s`, argument '
                                u'`%(argument_name)s`%(argument_position)s: '
                                u'%(message)s'),
                            params={
                                'message': message,
                                'contents': self.contents,
                                'argument_name': arg_name,
                                'argument_position': ' (pos %d)'
                                % arg_idx if arg_idx != -1 else u''})
                    else:
                        err = InlineValidationError(
                            lineno, _(u'Inline `%(contents)s`:  %(message)s'),
                            params={
                                'message': message, 'contents': self.contents})
                    errors.append(err)
        raise ValidationError(errors)


class TextNode(BaseNode):

    def __init__(self, token):
        super(TextNode, self).__init__(token)

    def render(self, media=None):
        return self.contents


class Parser(object):

    def __init__(self, media=None):
        self.media = media

    def parse(self, content):
        errors = []
        inline_nodes = []

        for token in Lexer(content).tokenize():
            if token.token_type == TOKEN_INLINE:
                try:
                    name, variant, args, kwargs = \
                        self.parse_inline_token(token)
                except InlineSyntaxError as err:
                    errors.append(err)
                    continue

                try:
                    inline_cls = registry.get_registered_inline(
                        name, variant=variant, media=self.media)
                except registry.NotRegistered:
                    errors.append(
                        InlineSyntaxError(
                            token.lineno,
                            _(u'Inline `%(inline_name)s` is not registered.'),
                            params={'inline_name': name}))
                    continue
                except registry.InvalidVariant:
                    errors.append(
                        InlineSyntaxError(
                            token.lineno,
                            _(u'`%(variant)s` is not a valid variant for '
                              u'inline `%(inline_name)s`'),
                            params={'variant': variant, 'inline_name': name}))
                    continue

                inline_nodes.append(
                    InlineNode(
                        InlineFactory(
                            inline_cls, name, args, kwargs), variant, token))
            else:
                inline_nodes.append(TextNode(token))
        return inline_nodes, errors

    def parse_inline_token(self, token):
        bits = token.split_contents()

        if len(bits) == 0:
            raise InlineSyntaxError(token.lineno, _(u'Empty inline found.'))

        args = []
        kwargs = {}
        in_kwargs = False
        ibits = bits.pop(0).split(':')
        name, variant = ibits if len(ibits) == 2 else (ibits[0], None,)

        for arg in bits:
            match = KWARG_RE.match(arg)
            if match:
                k, v = match.groups()
                try:
                    v = unescape_string_literal(v)
                except ValueError:
                    # Not a literal (i.e. doesn't start and end w\ ' or ")
                    pass
                if k is None:
                    if in_kwargs:
                        raise InlineSyntaxError(
                            token.lineno, _(
                                u'Inline `%(inline_content)s`, '
                                u'non-keyword argument found after keyword '
                                u'argument.'),
                            params={'inline_content': token.contents})
                    args.append(v)
                else:
                    in_kwargs = True
                    kwargs[k] = v
        return name, variant, args, kwargs
