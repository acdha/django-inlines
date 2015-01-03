from django.utils import six
from django.utils.translation import ugettext_lazy as _

from django.core.exceptions import (
    ObjectDoesNotExist, MultipleObjectsReturned, ValidationError,)

from .model_arguments import QueryArgument
from .inlines import InlineBase, InlineMetaClass, InlineOptions
from .template_inlines import TemplateInlineMixin

__all__ = ('ModelInlineBase', 'ModelInline', 'ModelTemplateInline',)


class ModelInlineOptions(InlineOptions):

    def __init__(self, meta, args, app_label):
        self.model = getattr(meta, 'model', None)
        super(ModelInlineOptions, self).__init__(meta, args, app_label)


class ModelInlineMetaClass(InlineMetaClass):

    def get_inline_options(cls, base_meta, meta, args, app_label=None):
        opts = ModelInlineOptions(meta, args, app_label)
        cls.carryover_options(base_meta, opts)
        return opts

    def carryover_options(cls, base_meta, opts):
        super(ModelInlineMetaClass, cls).carryover_options(base_meta, opts)
        if base_meta:
            base_meta_model = getattr(base_meta, 'model', None)
            if opts.model is None and base_meta_model is not None:
                opts.model = base_meta_model


class ModelInlineBase(InlineBase):

    def __init__(self, name, variant=None, *args, **kwargs):
        self.object = None

        if self._meta.model is None and not self._meta.abstract:
            raise ValueError(
                'Non-abstract ModelInline has no model class specified.')

        super(ModelInlineBase, self).__init__(name, variant, *args, **kwargs)

    def get_queryset(self):
        return self._meta.model._default_manager.get_queryset()

    def get_object(self):
        data = self.data

        query_args = dict((
            (arg.field, data[arg.name],)
            for arg in self._meta.args.values()
            if isinstance(arg, QueryArgument)))

        return self.get_queryset().get(**query_args)

    def process(self):
        super(ModelInlineBase, self).process()

        if bool(self._errors):
            return

        try:
            self.object = self.get_object()
        except ObjectDoesNotExist:
            self.add_errors(ValidationError(_('Object does not exist')))
        except MultipleObjectsReturned:
            self.add_errors(ValidationError(_('Multiple objects returned')))


class ModelTemplateInlineBase(TemplateInlineMixin, ModelInlineBase):

    def get_context(self):
        return {'object': self.object}


class ModelInline(six.with_metaclass(ModelInlineMetaClass, ModelInlineBase)):
    pass


class ModelTemplateInline(
        six.with_metaclass(ModelInlineMetaClass, ModelTemplateInlineBase)):
    pass
