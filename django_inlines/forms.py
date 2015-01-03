from django import forms

from .rendering import renderer

__all__ = ('InlineField',)


class InlineField(forms.CharField):
    widget = forms.Textarea(attrs={'cols': '79', 'rows': '50'})

    def validate(self, value):
        super(InlineField, self).validate(value)
        renderer.render(value, raise_errors=True)
