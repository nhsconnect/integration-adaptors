import os
from pathlib import Path

from PyInquirer import prompt
from utilities.file_utilities import FileUtilities

from adaptor.outgoing.config import operation_dict
from adaptor.outgoing.outgoing_adaptor import OutgoingAdaptor
from definitions import ROOT_DIR

nhais_mailbox_dir = Path(ROOT_DIR) / "mailbox" / "NHAIS"
gp_mailbox_dir = Path(ROOT_DIR) / "mailbox" / "GP"

# Determine the GP mailbox to read from
dirs = os.listdir(gp_mailbox_dir)
gp_outbox_choices = [
    {
        'type': 'list',
        'name': 'gp',
        'message': 'Select a GP outbox to read from: ',
        'choices': dirs
    }
]
answers = prompt(gp_outbox_choices)
gp_cypher = answers["gp"]

# Determine the fhir payload to read
gp_outbox_path = str(gp_mailbox_dir / gp_cypher / "outbox")
files = os.listdir(gp_outbox_path)
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

# Read the incoming file
incoming_file_path = f"{gp_outbox_path}/{file_name}"
patient_register_json = FileUtilities.get_file_dict(incoming_file_path)

# run the adaptor
adaptor = OutgoingAdaptor(operation_dict=operation_dict)
(sender, recipient, interchange_seq_no, edifact_interchange) = adaptor.convert_to_edifact(patient_register_json)

# create the generated edifact interchange
file_path_to_write = str(nhais_mailbox_dir / recipient / "inbox" / f"{sender}-{interchange_seq_no}.txt")
edifact_file = open(file_path_to_write, "w")
pretty_edifact_interchange = "'\n".join(edifact_interchange.split("'"))
edifact_file.write(pretty_edifact_interchange)
edifact_file.close()
