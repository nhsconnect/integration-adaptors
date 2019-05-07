import os
import json
from fhirclient.models.operationdefinition import OperationDefinition
import adaptor.outgoing.interchange_adaptor as adaptor
from PyInquirer import prompt

dirs = os.listdir("./mailbox/GP")

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

files = os.listdir(f"./mailbox/GP/{gp_cypher}/outbox")

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
print(file_name)

with open(f"./mailbox/GP/{gp_cypher}/outbox/{file_name}", "r") as patient_register:
    patient_register_json = json.load(patient_register)

op_def = OperationDefinition(patient_register_json)

(sender, recipient, interchange_seq_no, edifact_interchange) = adaptor.create_interchange(fhir_operation=op_def)

edifact_file = open(f"./mailbox/NHAIS/{recipient}/inbox/{sender}-{interchange_seq_no}.txt", "w")

pretty_edifact_interchange = "'\n".join(edifact_interchange.split("'"))

edifact_file.write(pretty_edifact_interchange)
edifact_file.close()
