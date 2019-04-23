from common.pystachemessagebuilder import PystacheMessageBuilder
from pathlib import Path
from definitions import ROOT_DIR


class SummaryCareRecord:

    summaryCareRecordPath = Path(ROOT_DIR) / "data/templates"

    def __init__(self):
        self.builder = PystacheMessageBuilder(str(self.summaryCareRecordPath), "16UK05")

    def populate_template(self, input_hash):
        """
        Given a python dictionary this method returns a xml string containing the populated template of the
        GP Summary Update template
        :param input_hash:
        :return: xml string containing populated template
        """
        return self.builder.build_message(input_hash)
