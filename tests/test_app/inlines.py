from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django_inlines import inlines

from .models import InlineTestModel

__all__ = ('BasicInlineParent', 'BasicInline', 'BasicMixInline',
           'BasicTemplateInline', 'MarkdownTemplateInline', 'BasicModelInline',
           'MultipleModelInline', 'BlankModelInline',
           'BasicModelTemplateInline',)


def validate_not_a_rebel(value):
    if value == 'rebel':
        raise ValidationError(
            _(u'Is a part of the Rebel Alliance and a traitor!'))


class BasicInlineParent(inlines.Inline):
    arg2 = inlines.Argument()
    arg1 = inlines.Argument()


class BasicInline(BasicInlineParent):
    CHOICE_ARG2 = u'arg2'
    CHOICE_KWARG2 = u'kwarg2'
    CHOICE_HOPE = u'hope'

    CHOICES = (
        (CHOICE_HOPE, _(u'Hope'),),
        (CHOICE_ARG2, _(u'Argument 2'),),
        (CHOICE_KWARG2, _(u'Keyword Argument 2'),),)

    arg2 = inlines.Argument(choices=CHOICES)
    arg1 = inlines.Argument()

    kwarg1 = inlines.Argument(keyword=True)
    kwarg2 = inlines.Argument(
        keyword=True, default=CHOICE_KWARG2, choices=CHOICES)
    kwarg3 = inlines.Argument(
        keyword=True, default='x@x.com',
        validators=[validate_email, validate_not_a_rebel])

    def clean(self):
        data = super(BasicInline, self).clean()

        if 'arg1' in data and 'arg2' in data:
            arg1 = data['arg1']
            arg2 = data['arg2']

            if arg1 == 'a new' and arg2 == 'hope':
                raise ValidationError(
                    _(u'You are a part of the Rebel Alliance and a traitor!'))

        return data

    def clean_arg1(self):
        arg1 = self.data['arg1']

        if arg1 == 'hope':
            raise ValidationError([
                ValidationError(_(u'Validation Error 1'), code='hope'),
                ValidationError(_(u'Validation Error 2'))])

        return arg1

    def mix_case(self, val, mod=2):
        return u''.join((
            ch.upper() if i % mod == 0 else ch.lower()
            for i, ch in enumerate(val)))

    def render(self):
        return self._render()

    def render_upper(self):
        return self._render().upper()

    def render_mix(self):
        return self.mix_case(self._render())

    def _render(self):
        return u'%(arg1)s %(arg2)s %(kwarg1)s %(kwarg2)s' % self.data

    class Meta(object):
        app_label = 'test_label'
        variants = ('upper', 'mix',)
        ordering = ('arg1', 'arg2',)


class BasicMixInline(BasicInline):
    def render_mix(self):
        return self.mix_case(self._render(), mod=4)


class BasicTemplateInline(inlines.TemplateInline):
    arg1 = inlines.Argument()

    def render_downer(self):
        return self.data['arg1'].lower()

    def get_context(self):
        return self.data

    class Meta(object):
        variants = ('downer',)
        app_label = 'test_app'


class MarkdownTemplateInline(BasicTemplateInline):
    def get_template_extension(self, variant=None, media=None):
        return 'md'

    class Meta(object):
        variants = ('upper',)
        app_label = 'test_app'


class BasicModelInline(inlines.ModelInline):
    id = inlines.IntegerQueryArgument(field='pk')

    def get_queryset(self):
        return InlineTestModel.objects.all()

    def _render(self):
        return self.object.text

    def render(self):
        return self._render()

    def render_upper(self):
        return self._render().upper()

    class Meta(object):
        variants = ('upper',)
        model = InlineTestModel
        app_label = 'test_app'


class BasicModelTemplateInlineP(inlines.ModelTemplateInline):
    id = inlines.IntegerQueryArgument(field='pk')

    def get_template_extension(self, variant=None, media=None):
        return 'md'

    class Meta(object):
        abstract = True
        variants = ('upper',)
        app_label = 'test_app'
        model = InlineTestModel


class BasicModelTemplateInline(BasicModelTemplateInlineP):
    pass


class BlankModelInline(inlines.ModelInline):
    pass


class MultipleModelInline(inlines.ModelInline):
    text = inlines.CharQueryArgument()

    class Meta(object):
        app_label = 'test_app'
        model = InlineTestModel
