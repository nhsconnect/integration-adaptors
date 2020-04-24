from edifact.edifact_exception import EdifactValidationException
from edifact.outgoing.models.segment import Segment


def required(inst: Segment, attribute_name):
    if not getattr(inst, attribute_name, None):
        raise EdifactValidationException(f'{inst.key}: Attribute {attribute_name} is required')