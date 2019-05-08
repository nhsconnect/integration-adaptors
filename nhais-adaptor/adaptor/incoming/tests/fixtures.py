import adaptor.fhir_helpers.fhir_creators as creators


def create_operation_definition_for_approval(recipient, transaction_number):
    sender_parameter = creators.create_parameter_with_binding(name="senderCypher", value="XX11",
                                                              direction="out")
    recipient_parameter = creators.create_parameter_with_binding(name="recipientCypher", value=recipient,
                                                                 direction="out")
    transaction_parameter = creators.create_parameter_with_binding(name="transactionNumber", value=transaction_number,
                                                                   direction="out")
    op_def = creators.create_operation_definition(name="Response-RegisterPatient-Approval",
                                                  code="gpc.registerpatient.approval",
                                                  date_time="2019-04-29 17:56",
                                                  parameters=[
                                                      sender_parameter,
                                                      recipient_parameter,
                                                      transaction_parameter
                                                  ])
    return op_def


def create_operation_definition_for_deduction(recipient, transaction_number, nhsNumber):
    sender_parameter = creators.create_parameter_with_binding(name="senderCypher", value="XX11",
                                                              direction="out")
    recipient_parameter = creators.create_parameter_with_binding(name="recipientCypher", value=recipient,
                                                                 direction="out")
    transaction_parameter = creators.create_parameter_with_binding(name="transactionNumber", value=transaction_number,
                                                                   direction="out")
    nhs_number_parameter = creators.create_parameter_with_binding(name="nhsNumber", value=nhsNumber,
                                                                  direction="out")
    op_def = creators.create_operation_definition(name="Response-RegisterPatient-Deduction",
                                                  code="gpc.registerpatient.deduction",
                                                  date_time="2019-04-29 17:56",
                                                  parameters=[
                                                      sender_parameter,
                                                      recipient_parameter,
                                                      transaction_parameter,
                                                      nhs_number_parameter
                                                  ])
    return op_def
