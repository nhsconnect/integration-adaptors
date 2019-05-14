import json
import os
from pathlib import Path

from PyInquirer import prompt
from utilities.file_utilities import FileUtilities

from adaptor.incoming.incoming_adaptor import IncomingAdaptor
from adaptor.incoming.operation_definition_adaptor import OperationDefinitionAdaptor
import edifact.incoming.parser.deserialiser as deserialiser
from definitions import ROOT_DIR
from adaptor.incoming.config import reference_dict

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

# Run the adaptor
adaptor = IncomingAdaptor(reference_dict)
op_defs = adaptor.covert_to_fhir(incoming_interchange_raw)

# create the generated fhir operation definitions files
for (transaction_number, recipient, op_def) in op_defs:

    file_path_to_write = str(gp_mailbox_dir / recipient / "inbox" / f"approval-{transaction_number}.json")
    with open(file_path_to_write, "w") as outfile:
        json.dump(op_def, outfile, indent=4)
