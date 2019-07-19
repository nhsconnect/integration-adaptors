import os
from unittest import TestCase

from builder.pystache_message_builder import PystacheMessageBuilder

TEMPLATES_DIR = "templates"
TEMPLATE_FILENAME = "test"


class TestPystacheMessageBuilder(TestCase):
    def setUp(self):
        current_dir = os.path.dirname(__file__)
        templates_dir = os.path.join(current_dir, TEMPLATES_DIR)

        self.builder = PystacheMessageBuilder(templates_dir, TEMPLATE_FILENAME)

    def test_build_message(self):
        message = self.builder.build_message(dict(to="world"))

        self.assertEqual("Hello, world!", message.strip(),
                         "Message returned should be the rendered string returned by Pystache")
