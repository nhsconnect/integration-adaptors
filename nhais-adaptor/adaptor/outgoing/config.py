from adaptor.fhir_helpers.fhir_creators import OperationName
from adaptor.outgoing.birth.message_birth_adaptor import MessageBirthAdaptor
from adaptor.outgoing.death.message_death_adaptor import MessageDeathAdaptor

operation_dict = {
    OperationName.REGISTER_BIRTH: {
        "messageAdaptor": MessageBirthAdaptor
    },
    OperationName.REGISTER_DEATH: {
        "messageAdaptor": MessageDeathAdaptor
    }
}
