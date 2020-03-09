"""A module that defines a Pystache-based MessageBuilder."""
import pystache
from pystache import common as pystache_common
from pystache import context as pystache_context

import utilities.integration_adaptors_logger as log

logger = log.IntegrationAdaptorsLogger(__name__)


class PystacheMessageBuilder(object):
    """A component that uses Pystache to populate a Mustache template in order to build a message."""

    def __init__(self, template_dir, template_file):
        """Create a new PystacheMessageBuilder that uses the specified template file.

        ** Note: Is it expected behavior that pystache should fail if there are missing tags - This should not be
        ** changed without strong reason as it is the mechanism for assuring message contents is valid within other
        ** services.
        :param template_dir: The directory to load template files from
        :param template_file: The template file to populate with values.
        """
        self._renderer = pystache.Renderer(search_dirs=template_dir, missing_tags=pystache_common.MissingTags.strict)
        self.template_file = template_file
        raw_template = self._renderer.load_template(template_file)
        self._parsed_template = pystache.parse(raw_template)

    def build_message(self, message_dictionary):
        """Build a message by populating a Mustache template with values from the provided dictionary.
        :param message_dictionary: The dictionary of values to use when populating the template.
        :return: A string containing a message suitable for sending to a remote MHS.
        """
        try:
            return self._renderer.render(self._parsed_template, message_dictionary)
        except pystache_context.KeyNotFoundError as e:
            logger.error('Failed to find {Key} when generating message from {TemplateFile} . {ErrorMessage}',
                         fparams={'Key': e.key, 'TemplateFile': self.template_file, 'ErrorMessage': e})
            raise MessageGenerationError(f'Failed to find key:{e.key} when generating message from'
                                         f' template file:{self.template_file}') from e


class MessageGenerationError(Exception):
    """
    An exception generated when an error is encountered during message generation.
    """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
