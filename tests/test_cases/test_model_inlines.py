from django.core.exceptions import ValidationError

from django_inlines import registry, renderer

from test_app.models import InlineTestModel
from test_app.inlines import (
    BasicModelInline, BlankModelInline, MultipleModelInline,
    BasicModelTemplateInline,)

from .test_common import InlinesTestCase

__all__ = ('ModelInlineTestCase', 'ModelTemplateInlineTestCase',)


class ModelInlineTestCase(InlinesTestCase):

    def test_model_inline(self):
        registry.register('model', BasicModelInline)

        obj = InlineTestModel.objects.create(text='Test')

        self.assertEqual(
            u'Test', renderer.render(u'{{ model %s }}' % obj.pk))

        self.assertEqual(
            u'TEST', renderer.render(
                u'{{ model:upper %s }}' % obj.pk, raise_errors=True))

    def test_arg_validation_error(self):
        registry.register('model', BasicModelInline)

        self.assertRaisesMessage(
            ValidationError,
            u'Inline `model 1 2`:  Takes only 1 non-keyword argument '
            u'(2 given).', renderer.render, u'{{ model 1 2 }}',
            None, True)

    def test_object_does_not_exist(self):
        registry.register('model', BasicModelInline)

        self.assertRaisesMessage(
            ValidationError,
            u'Inline `model 1`:  Object does not exist',
            renderer.render, u'{{ model 1 }}', None, True)

    def test_multiple_objects_returned(self):
        registry.register('model_multiple', MultipleModelInline)

        InlineTestModel.objects.bulk_create((
            InlineTestModel(text='Test'),
            InlineTestModel(text='Test'),))

        self.assertRaisesMessage(
            ValidationError,
            u'Inline `model_multiple Test`:  Multiple objects returned',
            renderer.render,
            u'{{ model_multiple Test }}', None, True)

    def test_blank_model_inline(self):
        with self.assertRaises(ValueError) as cm:
            BlankModelInline('blank')


class ModelTemplateInlineTestCase(InlinesTestCase):

    def test_model_template_inline(self):
        registry.register('model_template_inline', BasicModelTemplateInline)

        obj = InlineTestModel.objects.create(text='Test')

        self.assertEqual(
            u'**Test**',
            renderer.render(
                u'{{ model_template_inline %s }}' % obj.pk, raise_errors=True))

        self.assertEqual(
            u'**TEST**',
            renderer.render(
                u'{{ model_template_inline:upper %s }}' % obj.pk,
                raise_errors=True))
