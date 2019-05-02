PARTY_ID = "A91424-9199121"

WRAPPER_REQUIRED = 'ebxml_wrapper_required'
FROM_PARTY_ID = "from_party_id"
MESSAGE = "hl7_message"


class Sender:
    def __init__(self, interactions_config, message_builder, transport):
        """Create a new Sender that uses the specified dependencies to load config, build a message and send it.

        :param interactions_config: The object that can be used to obtain interaction-specific configuration details.
        :param message_builder: The message builder that can be used to build a message.
        :param transport: The transport that can be used to send messages.
        """

        self.interactions_config = interactions_config
        self.message_builder = message_builder
        self.transport = transport

    def send_message(self, interaction_name, message_to_send):
        """Send the specified message for the interaction named.

        :param interaction_name: The name of the interaction the message is related to.
        :param message_to_send: A string representing the message to be sent.
        :return: The content of the response received when the message was sent.
        """

        interaction_details = self.interactions_config.get_interaction_details(interaction_name)

        requires_ebxml_wrapper = interaction_details[WRAPPER_REQUIRED]
        if requires_ebxml_wrapper:
            context = interaction_details.copy()
            context[FROM_PARTY_ID] = PARTY_ID
            context[MESSAGE] = message_to_send

            message = self.message_builder.build_message(context)
        else:
            message = message_to_send

        response = self.transport.make_request(interaction_details, message)

        return response
