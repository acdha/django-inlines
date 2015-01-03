from os import path

from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string

from .inlines import Inline

__all__ = ('TemplateInlineMixin', 'TemplateInline',)


class TemplateInlineMixin(object):

    def get_context(self):
        return {}

    def get_full_context(self):
        ctx = {'inline': self.data}
        ctx.update(self.get_context())
        return ctx

    def get_template_extension(self, variant=None, media=None):
        return 'html'

    def get_templates(self, variant=None, media=None):
        base_templates = []

        base_tmpl_dir = 'inlines'
        app_label = self._meta.app_label

        template_path_options = {
            'name': self.name,
            'variant': variant,
            'cls_name': self.__class__.__name__.lower(),
            'ext': self.get_template_extension(variant=variant, media=media)}

        if variant is not None:
            base_templates.extend((
                path.join(
                    app_label,
                    '%(name)s__%(variant)s.%(ext)s' % template_path_options),
                path.join(
                    app_label, '%(cls_name)s__%(variant)s.%(ext)s'
                    % template_path_options),
                '%(name)s__%(variant)s.%(ext)s' % template_path_options,
                '%(cls_name)s__%(variant)s.%(ext)s' % template_path_options,))

        base_templates.extend((
            path.join(
                app_label, '%(name)s.%(ext)s' % template_path_options),
            '%(name)s.%(ext)s' % template_path_options,
            path.join(
                app_label, '%(cls_name)s.%(ext)s' % template_path_options),
            '%(cls_name)s.%(ext)s' % template_path_options))

        templates = [
            path.join(base_tmpl_dir, tmpl) for tmpl in base_templates]

        if media is not None:
            templates = [
                path.join(base_tmpl_dir, media, tmpl)
                for tmpl in base_templates] + templates

        return templates

    def full_render(self, variant=None, media=None):
        renderer = getattr(self, 'render_%s' % variant, None)

        if renderer is not None:
            return renderer()

        try:
            return render_to_string(
                self.get_templates(variant=variant, media=media),
                self.get_full_context())
        except TemplateDoesNotExist as err:
            try:
                return self.render()
            except NotImplementedError:
                raise err


class TemplateInline(TemplateInlineMixin, Inline):
    pass
