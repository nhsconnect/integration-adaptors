import os
import json
from pathlib import Path
import adaptor.incoming.operation_definition_adaptor as adaptor
import edifact.incoming.parser.deserialiser as deserialiser
from utilities.file_utilities import FileUtilities
from PyInquirer import prompt

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
nhais_mailbox_dir = Path(ROOT_DIR) / "mailbox" / "NHAIS"
gp_mailbox_dir = Path(ROOT_DIR) / "mailbox" / "GP"

# Determine the NHAIS mailbox to read from
dirs = os.listdir(nhais_mailbox_dir)
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

# Determine the fhir payload to read
nhais_outbox_path = str(nhais_mailbox_dir / nhais_cypher / "outbox")
files = os.listdir(nhais_outbox_path)
file_choices = [
    {
        'type': 'list',
        'name': 'file',
        'message': 'Select a file: ',
        'choices': files
    }
]
file_answer = prompt(file_choices)
file_name = file_answer["file"]

# read the incoming file
incoming_file_path = f"{nhais_outbox_path}/{file_name}"
incoming_interchange_raw = FileUtilities.get_file_string(incoming_file_path)

# deserialise the incoming edifact interchange
lines = incoming_interchange_raw.split("'\n")
interchange = deserialiser.convert(lines)

# Run the adaptor
op_defs = adaptor.create_operation_definition(interchange)

# create the generated fhir operation definitions files
for (transaction_number, recipient, op_def) in op_defs:
    pretty_op_def = op_def.as_json()

    file_path_to_write = str(gp_mailbox_dir / recipient / "inbox" / f"approval-{transaction_number}.json")
    with open(file_path_to_write, "w") as outfile:
        json.dump(pretty_op_def, outfile, indent=4)

