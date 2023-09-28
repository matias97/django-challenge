from rest_framework.renderers import JSONRenderer

# for simplicity to avoid using templates I'm using a custom JSON renderer
class PlainJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        return super().render(data, 'application/json')
