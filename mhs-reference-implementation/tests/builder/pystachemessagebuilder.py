from unittest import TestCase
from unittest.mock import patch, sentinel

from mhs.builder.pystachemessagebuilder import PystacheMessageBuilder, Renderer

TEMPLATE_DIR = "TEMPLATE_DIR"

TEMPLATE_FILENAME = "template_file"


class PystacheMessageBuilderTest(TestCase):
    @patch("pystache.parse")
    @patch("mhs.builder.pystachemessagebuilder.Renderer")
    def test_build_message(self, mock_renderer, mock_parse):
        renderer_instance = mock_renderer.return_value
        renderer_instance.render.return_value = sentinel.rendered_string
        mock_parse.return_value = sentinel.parsed_template

        builder = PystacheMessageBuilder(TEMPLATE_DIR, TEMPLATE_FILENAME)
        message = builder.build_message(sentinel.message_dictionary)

        renderer_instance.render.assert_called_with(sentinel.parsed_template, sentinel.message_dictionary)
        self.assertIs(sentinel.rendered_string, message,
                      "Message returned should be the rendered string returned by pystache")
