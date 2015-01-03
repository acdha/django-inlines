from django_inlines import registry

from test_app.inlines import BasicInline, BasicMixInline

from .test_common import InlinesTestCase

__all__ = ('InlineRegisteryTestCase',)


class InlineRegisteryTestCase(InlinesTestCase):

    def test_registration(self):
        registry.register('echo', BasicInline)
        registry.register(('echo1', 'echo2', 'echo3',), BasicInline)

        for inline in ('echo', 'echo1', 'echo2', 'echo3',):
            self.assertEqual(
                BasicInline, registry.get_registered_inline(inline))

    def test_unregister(self):
        inline_names = ('echo', 'echo1', 'echo2',)
        registry.register(inline_names, BasicInline)

        registry.unregister('echo')

        with self.assertRaises(registry.NotRegistered):
            registry.get_registered_inline('echo')

        registry.unregister(('echo1', 'echo2',))

        self.__test_inlines_not_registered(inline_names)

    def test_registry_clear(self):
        inline_names = ('echo1', 'echo2',)
        registry.register(inline_names, BasicInline)

        registry.clear()

        self.__test_inlines_not_registered(inline_names)

    def test_already_registered(self):
        registry.register('echo', BasicInline)

        with self.assertRaises(registry.AlreadyRegistered):
            registry.register('echo', BasicInline)

    def test_register_media(self):
        registry.register(
            'echo', BasicInline, media={'media': BasicMixInline})

    def test_not_registered(self):
        with self.assertRaises(registry.NotRegistered):
            registry.get_registered_inline('echo')
        with self.assertRaises(registry.NotRegistered):
            registry.unregister('echo')

    def __test_inlines_not_registered(self, inline_names):
        for inline_name in inline_names:
            with self.assertRaises(registry.NotRegistered):
                registry.get_registered_inline(inline_name)
