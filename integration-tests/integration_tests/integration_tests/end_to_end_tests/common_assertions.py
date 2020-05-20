from integration_tests.amq.amq_message_assertor import AMQMessageAssertor
from integration_tests.db.mhs_table import MhsTableStateAssertor
from integration_tests.xml.hl7_xml_assertor import Hl7XmlResponseAssertor


class CommonAssertions(object):
    def __init__(self, workflow):
        self.workflow = workflow

    def spline_reply_published_to_message_queue(self, amq_assertor: AMQMessageAssertor, message_id):
        """
        Verifies that the message queue contains an inbound response with the specified message id
        @param amq_assertor: the assertor instance
        @param message_id: message id to look for
        """
        amq_assertor \
            .assert_property('message-id', message_id) \
            .assert_property('correlation-id', '1') \
            .assert_json_content_type()

    def message_status_recorded_as_successfully_processed(self, state_table_assertor: MhsTableStateAssertor, message_id):
        return state_table_assertor \
            .assert_single_item_exists_with_key(message_id) \
            .assert_item_contains_values({
                'INBOUND_STATUS': 'INBOUND_RESPONSE_SUCCESSFULLY_PROCESSED',
                'OUTBOUND_STATUS': 'OUTBOUND_MESSAGE_ACKD',
                'WORKFLOW': f'{self.workflow}'
        })

    def hl7_xml_contains_response_code_and_patient_id(self, hl7_xml_message_assertor: Hl7XmlResponseAssertor):
        hl7_xml_message_assertor \
            .assert_element_attribute('.//queryAck//queryResponseCode', 'code', 'OK') \
            .assert_element_attribute('.//patient//id', 'extension', '9691035456')
