import sys

from collections import defaultdict, OrderedDict

from django.core.exceptions import ValidationError

from django.utils import six
from django.utils.translation import ugettext_lazy as _, ungettext_lazy as _n

from .arguments import Argument

__all__ = ('InlineOptions', 'InlineMetaClass', 'InlineBase', 'Inline',)


class InlineOptions(object):

    def __init__(self, meta, args, app_label):
        self.meta = meta
        self.args = args
        self.ordering = []
        self.variants = []
        self.app_label = app_label
        self.abstract = getattr(meta, 'abstract', False)

    def _prepare(self, inline_mcs):
        args = inline_mcs._meta.args

        for arg_name, arg in args.items():
            arg.name = arg_name

        if hasattr(self.meta, 'variants'):
            self.variants = list(self.meta.variants)

        if hasattr(self.meta, 'ordering'):
            ordering = list(OrderedDict(
                (order, True) for order in self.meta.ordering).keys())
            for arg in ordering:
                assert arg in args, '`%s` is not a valid argument' % arg
                assert not args[arg].keyword, \
                    '`ordering` may not include keyword arguments'
            self.ordering = ordering
        elif not bool(self.ordering):
            self.ordering = [
                key for key, val in args.items() if not val.keyword]

        self.num_required_args = len(self.ordering)


class InlineMetaClass(type):

    def __new__(mcs, name, bases, attrs):
        super_new = super(InlineMetaClass, mcs).__new__

        if name == 'NewBase' and attrs == {}:
            return super_new(mcs, name, bases, attrs)

        parents = [
            b for b in bases if isinstance(b, InlineMetaClass) and
            not (b.__name__ == 'NewBase' and b.__mro__ == (b, object))]

        if not parents:
            return super_new(mcs, name, bases, attrs)

        module = attrs.pop('__module__')
        new_class = super_new(mcs, name, bases, {'__module__': module})

        attr_meta = attrs.pop('Meta', None)

        if not attr_meta:
            meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta

        args = []
        base_meta = getattr(new_class, '_meta', None)

        for item in attrs.items():
            attr_name, attr = item
            if isinstance(attr, Argument):
                attrs.pop(attr_name)
                args.append(item)

        args.sort(key=lambda x: x[1].creation_counter)

        args = OrderedDict(args)

        for base in reversed(new_class.__mro__):
            if hasattr(base, '_meta'):
                for arg_name, arg in base._meta.args.items():
                    if arg_name not in args:
                        args[arg_name] = arg

        app_label = getattr(meta, 'app_label', None)

        if app_label is None:
            inline_module = sys.modules[new_class.__module__]
            app_label = inline_module.__name__.split('.')[-2]

        setattr(
            new_class, '_meta',
            new_class.get_inline_options(base_meta, meta, args, app_label))

        for obj_name, obj in attrs.items():
            setattr(new_class, obj_name, obj)

        new_class._prepare()

        return new_class

    def _prepare(cls):
        cls._meta._prepare(cls)

    def get_inline_options(cls, base_meta, meta, args, app_label):
        opts = InlineOptions(meta, args, app_label)
        cls.carryover_options(base_meta, opts)
        return opts

    def carryover_options(cls, base_meta, opts):
        if base_meta:
            if not bool(opts.ordering):
                opts.ordering = base_meta.ordering
            if not bool(opts.variants):
                opts.variants = base_meta.variants


class InlineBase(object):

    def full_render(self, variant=None, media=None):
        renderer = getattr(self, 'render_%s' % variant, self.render)
        return renderer()

    def render(self):
        raise NotImplementedError

    def __init__(self, name, *args, **kwargs):
        self.name = name

        self.raw_args = args
        self.raw_kwargs = kwargs

        self._errors = None
        self.data = {}

    @property
    def errors(self):
        if self._errors is None:
            self.process()

        return self._errors

    def is_valid(self):
        return not bool(self.errors)

    def process(self):
        self._errors = defaultdict(list)
        raw_args_len = len(self.raw_args)
        inline_args_len = self._meta.num_required_args

        if raw_args_len < inline_args_len:
            self.add_errors(
                ValidationError(_n(
                    u'Takes at least %(inline_args_len)d non-keyword argument '
                    u'(%(raw_args_len)d given).',
                    u'Takes at least %(inline_args_len)d non-keyword '
                    u'arguments (%(raw_args_len)d given).', inline_args_len),
                    params={
                        'raw_args_len': raw_args_len,
                        'inline_args_len': inline_args_len}))
            return
        elif raw_args_len > inline_args_len:
            self.add_errors(
                ValidationError(_n(
                    u'Takes only %(inline_args_len)d non-keyword argument '
                    u'(%(raw_args_len)d given).',
                    u'Takes only %(inline_args_len)d non-keyword arguments'
                    u' (%(raw_args_len)d given).', inline_args_len),
                    params={
                        'raw_args_len': raw_args_len,
                        'inline_args_len': inline_args_len}))
            return

        args = OrderedDict(self._meta.args)
        raw_kwargs = self.raw_kwargs.copy()

        for i, arg_name in enumerate(self._meta.ordering):
            arg = args.pop(arg_name)

            try:
                self.data[arg_name] = arg.process(self.raw_args[i])
            except ValidationError as e:
                self.add_errors(e, arg_name)

        for arg_name, arg in args.items():
            try:
                val = raw_kwargs.pop(arg_name, arg.default)
                self.data[arg_name] = arg.process(val)
            except ValidationError as e:
                self.add_errors(e, arg_name)

        if bool(raw_kwargs):
            for arg_name in raw_kwargs.keys():
                self.add_errors(
                    ValidationError(_(
                        u'Got an unexpected keyword argument `%(arg_name)s`'),
                        params={'arg_name': arg_name}))

        self._clean_fields()
        self._clean_inline()

    def _clean_fields(self):
        for arg_name, _ in self._meta.args.items():
            try:
                if hasattr(self, 'clean_%s' % arg_name):
                    value = getattr(self, 'clean_%s' % arg_name)()
                    self.data[arg_name] = value
            except ValidationError as e:
                self.add_errors(e, arg_name)

    def _clean_inline(self):
        try:
            data = self.clean()
        except ValidationError as e:
            self.add_errors(e)
        else:
            if data is not None:
                self.data = data

    def clean(self):
        return self.data

    def add_errors(self, errors, arg=None):
        for msg in errors.messages:
            self._errors[arg].append(ValidationError(msg))

    def get_argument_index(self, arg):
        try:
            return self._meta.ordering.index(arg) + 1
        except ValueError:
            return -1


class Inline(six.with_metaclass(InlineMetaClass, InlineBase)):
    pass
