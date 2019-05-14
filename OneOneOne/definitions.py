import os
from pathlib import Path

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
XML_PATH = Path(ROOT_DIR) / 'data' / 'response_xmls'
TEMPLATE_PATH = Path(ROOT_DIR) / 'data' / 'response_templates'
