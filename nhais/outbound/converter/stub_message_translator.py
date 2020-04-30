from fhir.resources.patient import Patient

from outbound.converter.base_message_translator import BaseMessageTranslator


class StubMessageTranslator(BaseMessageTranslator):
    def _append_transaction_type(self):
        pass

    def _append_message_body(self, patient: Patient):
        pass