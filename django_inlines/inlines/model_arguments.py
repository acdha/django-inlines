from .arguments import *

__all__ = (
    'QueryArgument', 'BooleanQueryArgument', 'NullBooleanQueryArgument',
    'CharQueryArgument', 'EmailQueryArgument', 'IntegerQueryArgument',
    'RegexQueryArgument', 'SlugQueryArgument', 'URLQueryArgument',
    'DecimalQueryArgument', 'FloatQueryArgument',)


class QueryArgument(Argument):

    def __init__(self, field=None, *args, **kwargs):
        self._field = field
        super(QueryArgument, self).__init__(*args, **kwargs)

    @property
    def field(self):
        return self._field if self._field is not None else self.name


class BooleanQueryArgument(BooleanArgument, QueryArgument):
    pass


class NullBooleanQueryArgument(NullBooleanArgument, QueryArgument):
    pass


class CharQueryArgument(CharArgument, QueryArgument):
    pass


class EmailQueryArgument(EmailArgument, QueryArgument):
    pass


class IntegerQueryArgument(IntegerArgument, QueryArgument):
    pass


class RegexQueryArgument(RegexArgument, QueryArgument):
    pass


class SlugQueryArgument(SlugArgument, QueryArgument):
    pass


class URLQueryArgument(URLArgument, QueryArgument):
    pass


class DecimalQueryArgument(DecimalArgument, QueryArgument):
    pass


class FloatQueryArgument(FloatArgument, QueryArgument):
    pass
