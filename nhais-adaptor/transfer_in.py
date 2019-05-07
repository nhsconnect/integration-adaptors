import os
import json
import adaptor.incoming.operation_definition_adaptor as adaptor
import edifact.incoming.parser.deserialiser as deserialiser
from PyInquirer import prompt

dirs = os.listdir("./mailbox/NHAIS")

nhais_outbox_choices = [
    {
        'type': 'list',
        'name': 'nhais',
        'message': 'Select a NHAIS outbox to read from: ',
        'choices': dirs
    }
]

answers = prompt(nhais_outbox_choices)
nhais_cypher = answers["nhais"]

with open(f"./mailbox/NHAIS/{nhais_cypher}/outbox/edifact.txt", "r") as incoming_edifact_file:
    incoming_interchange_raw = incoming_edifact_file.read()

lines = incoming_interchange_raw.split("'\n")
interchange = deserialiser.convert(lines)

op_defs = adaptor.create_operation_definition(interchange)

for (transaction_number, recipient, op_def) in op_defs:
    pretty_op_def = op_def.as_json()

    with open(f"./mailbox/GP/{recipient}/inbox/approval-{transaction_number}.json", "w") as outfile:
        json.dump(pretty_op_def, outfile, indent=4)

