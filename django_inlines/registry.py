from threading import RLock

from django.utils import six

__all__ = ('InlineRegistryItem', 'InlineRegistry', 'registry',)


class InvalidVariant(Exception):
    pass


class InlineRegistryItem(object):

    def __init__(self, default_inline_cls, media=None):
        self.default_inline_cls = default_inline_cls
        self._variants = set(default_inline_cls._meta.variants)
        if media is not None:
            self._media = dict(
                (k, (v, set(v._meta.variants),),) for k, v in media.items())
        else:
            self._media = {}

    def get_inline_cls(self, variant=None, media=None):
        if variant is not None and variant not in self._variants:
            raise InvalidVariant('Unknown variant `%s`' % variant)

        if media is not None:
            if media in self._media:
                media_cls, media_variants = self._media[media]

                if variant is None or variant in media_variants:
                    return media_cls

        return self.default_inline_cls


class InlineRegistry(object):

    class NotRegistered(Exception):
        pass

    class AlreadyRegistered(Exception):
        pass

    class InvalidVariant(InvalidVariant):
        pass

    def __init__(self):
        self._lock = RLock()
        self._registry = {}

    def clear(self):
        with self._lock:
            self._registry.clear()

    def register(self, inline_slugs, inline_cls, media=None):
        if isinstance(inline_slugs, six.string_types):
            inline_slugs = [inline_slugs]

        with self._lock:
            iri = InlineRegistryItem(inline_cls, media)

            for inline_slug in inline_slugs:
                if inline_slug in self._registry:
                    raise self.AlreadyRegistered(
                        'Inline `%s` is already registered' % inline_slug)
                self._registry[inline_slug] = iri

    def unregister(self, inline_slugs):
        if isinstance(inline_slugs, six.string_types):
            inline_slugs = [inline_slugs]

        with self._lock:
            for inline_slug in inline_slugs:
                try:
                    del self._registry[inline_slug]
                except KeyError:
                    raise self.NotRegistered(
                        'Inline `%s` is not registered' % inline_slug)

    def get_registered_inline(self, inline_slug, variant=None, media=None):
        try:
            with self._lock:
                return self._registry[inline_slug] \
                    .get_inline_cls(variant=variant, media=media)
        except KeyError:
            raise self.NotRegistered(
                'Inline `%s` is not registered' % inline_slug)
        except InvalidVariant:
            raise self.InvalidVariant('Unknown variant `%s`' % variant)


registry = InlineRegistry()
