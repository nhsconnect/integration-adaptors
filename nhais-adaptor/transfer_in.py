import json
import adaptor.incoming.operation_definition_adaptor as adaptor
import edifact.incoming.parser.deserialiser as deserialiser

with open("./mailbox/NHAIS/XX11/outbox/edifact.txt", "r") as incoming_edifact_file:
    incoming_interchange_raw = incoming_edifact_file.read()

lines = incoming_interchange_raw.split("'\n")
interchange = deserialiser.convert(lines)

op_def = adaptor.create_operation_definition(interchange)
pretty_op_def = op_def.as_json()

with open("./mailbox/GP/TES5/inbox/approval.json", "w") as outfile:
    json.dump(pretty_op_def, outfile, indent=4)

