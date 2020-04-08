"""
Schema definition for the request body that MHS accepts. To use this module, simply do:

.. code-block:: python

    try:
        request_body = RequestBodySchema().loads(body)
    except json.JSONDecodeError as e:
        ... # handle JSON decode errors
    except marshmallow.ValidationError as e:
        ... # handle validation errors
"""
import dataclasses
from typing import List

import marshmallow.validate

@dataclasses.dataclass
class RequestBody:
    """Dataclass representing the request body that NHAIS accepts. `RequestBodySchema` deserialises to this class."""
    payload: str

class RequestBodySchema(marshmallow.Schema):
    """Schema for the request body that NHAIS accepts"""
    payload = marshmallow.fields.Str(required=True, description='HL7 Payload to send to Spine',
                                     # No explicit documentation was found in the EIS as to the max size of this
                                     # HL7 payload, but additional attachments have a max size of 5MB so just set to
                                     # this. Note that the whole request body sent to Spine gets checked later to make
                                     # sure it isn't too large.
                                     validate=marshmallow.validate.Length(min=1, max=5_000_000))

    @marshmallow.post_load
    def make_request_body(self, data, **kwargs):
        return RequestBody(data['payload'], data['attachments'])
