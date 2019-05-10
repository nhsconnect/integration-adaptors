
def create_interchange_header_line():
    return ["UNB+UNOA:2+SO01+ROO5+190429:1756+00016288++FHSREG+++FHSA EDI TRANSFERS"]


def create_interchange_trailer_line():
    return ["UNZ+1+00016288"]


def create_message_header_line():
    return ["UNH+00024986+FHSREG:0:1:FH:FHS001"]


def create_message_trailer_line():
    return ["UNT+9+00024986"]


def create_message_beginning_lines(reference_number):
    return [
        "BGM+++507",
        "NAD+FHS+SO:954",
        "DTM+137:201904291755:203",
        f"RFF+950:{reference_number}",
    ]


def create_transaction_registration_lines(transaction_number):
    return [
        "S01+1",
        f"RFF+TN:{transaction_number}",
        "NAD+GP+1231231,PLP348:900",
    ]


def create_transaction_patient_lines(nhs_number):
    return [
        "S02+2",
        f"PNA+PAT+{nhs_number}:OPI",
    ]