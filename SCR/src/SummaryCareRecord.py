from common.pystachemessagebuilder import PystacheMessageBuilder
from common.utilities import Utilities
from pathlib import Path
from definitions import ROOT_DIR


class SummaryCareRecord:

    summaryCareRecordPath = Path(ROOT_DIR) / "src/MustacheTemplates"

    def __init__(self):
        self.builder = PystacheMessageBuilder(str(self.summaryCareRecordPath), "16UK05")

    def render_hash(self, input_hash):
        return self.builder.build_message(input_hash)
