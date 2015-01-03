from django.conf import settings
from django.template.base import TemplateDoesNotExist

from django_inlines import registry, renderer

from test_app.inlines import BasicTemplateInline, MarkdownTemplateInline

from .test_common import InlinesTestCase

__all__ = ('TemplateInlineTestCase',)


class TemplateInlineTestCase(InlinesTestCase):

    def setUp(self):
        registry.register('echo_template', BasicTemplateInline)

    def test_template_render(self):
        registry.register('echo_markdown', MarkdownTemplateInline)

        self.assertEqual(
            u'**Hello**', renderer.render(
                u'{{ echo_markdown Hello }}', raise_errors=True))

        self.assertEqual(
            u'**HELLO**', renderer.render(
                u'{{ echo_markdown:upper Hello }}', raise_errors=True))

    def test_missing_template_render(self):
        self.assertRaises(
            TemplateDoesNotExist, renderer.render,
            u'{{ echo_template arg1 }}', None, True)

        settings.INLINE_DEBUG = False

        self.assertEqual(
            u'', renderer.render(
                u'{{ echo_template arg1 }}',
                raise_errors=True, log_errors=False))

    def test_basic_template_order(self):
        inline = BasicTemplateInline('echo_template', 'arg1')

        templates = [
            'inlines/test_app/echo_template.html',
            'inlines/echo_template.html',
            'inlines/test_app/basictemplateinline.html',
            'inlines/basictemplateinline.html']

        media_templates = [
            'inlines/media/test_app/echo_template.html',
            'inlines/media/echo_template.html',
            'inlines/media/test_app/basictemplateinline.html',
            'inlines/media/basictemplateinline.html'] + templates

        self.assertEqual(templates, inline.get_templates())
        self.assertEqual(
            media_templates, inline.get_templates(media='media'))

    def test_variant_template_order(self):
        inline = MarkdownTemplateInline('echo_template', 'arg1')

        templates = [
            'inlines/test_app/echo_template.md',
            'inlines/echo_template.md',
            'inlines/test_app/markdowntemplateinline.md',
            'inlines/markdowntemplateinline.md']

        variant_templates = [
            'inlines/test_app/echo_template__variant.md',
            'inlines/test_app/markdowntemplateinline__variant.md',
            'inlines/echo_template__variant.md',
            'inlines/markdowntemplateinline__variant.md'] + templates

        _media_templates = [
            'inlines/media/test_app/echo_template.md',
            'inlines/media/echo_template.md',
            'inlines/media/test_app/markdowntemplateinline.md',
            'inlines/media/markdowntemplateinline.md']

        _media_variant_templates = [
            'inlines/media/test_app/echo_template__variant.md',
            'inlines/media/test_app/markdowntemplateinline__variant.md',
            'inlines/media/echo_template__variant.md',
            'inlines/media/markdowntemplateinline__variant.md']

        media_templates = _media_templates + templates

        media_variant_templates = \
            _media_variant_templates + _media_templates + variant_templates

        self.assertEqual(
            variant_templates,
            inline.get_templates(variant='variant'))
        self.assertEqual(
            media_variant_templates,
            inline.get_templates(variant='variant', media='media'))

    def test_template_override(self):
        self.assertEqual(
            u'arg1', renderer.render(
                u'{{ echo_template:downer ARG1 }}', raise_errors=True))
