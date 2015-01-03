from django.db import models

__all__ = ('InlineTestModel',)


class InlineTestModel(models.Model):
    text = models.CharField(max_length=70)
