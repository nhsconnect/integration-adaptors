class LineBuilder:

    def __init__(self):
        self.lines = []

    def start_interchange(self):
        self.lines.extend(["UNB+UNOA:2+SO01+ROO5+190429:1756+00016288++FHSREG+++FHSA EDI TRANSFERS"])
        return self

    def start_message(self, reference_number):
        self.lines.extend([
            "UNH+00024986+FHSREG:0:1:FH:FHS001",
            "BGM+++507",
            "NAD+FHS+SO:954",
            "DTM+137:201904291755:203",
            f"RFF+950:{reference_number}",
        ])
        return self

    def add_transaction(self, transaction_number, nhs_number=None):
        self.lines.extend([
            "S01+1",
            f"RFF+TN:{transaction_number}",
            "NAD+GP+1231231,PLP348:900",
        ])

        if nhs_number:
            self.lines.extend([
                "S02+2",
                f"PNA+PAT+{nhs_number}:OPI"
            ])
        return self

    def end_message(self):
        self.lines.extend(["UNT+9+00024986"])
        return self

    def end_interchange(self):
        self.lines.extend(["UNZ+1+00016288"])
        return self

    def build(self):
        return self.lines
