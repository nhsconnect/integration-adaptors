import dataclasses
from typing import List

import marshmallow.validate

# These allowed content types for attachments are taken from the EIS part 2.5.4.2
_ATTACHMENT_ALLOWED_CONTENT_TYPES = (
    'text/plain', 'text/html', 'application/pdf', 'text/xml', 'application/xml', 'text/rtf', 'audio/basic',
    'audio/mpeg', 'image/png', 'image/gif', 'image/jpeg', 'image/tiff', 'video/mpeg', 'application/msword'
)


@dataclasses.dataclass
class Attachment:
    is_base64: bool
    content_type: str
    payload: str


class AttachmentSchema(marshmallow.Schema):
    is_base64 = marshmallow.fields.Bool(required=True,
                                        description='Whether the attachment payload is base64-encoded or not. This is '
                                                    'only required for binary attachments eg images.',
                                        truthy={True}, falsy={False})
    content_type = marshmallow.fields.Str(required=True, description='Content type of the attachment',
                                          validate=marshmallow.validate.OneOf(_ATTACHMENT_ALLOWED_CONTENT_TYPES))
    payload = marshmallow.fields.Str(required=True,
                                     description='The attachment, possibly base64-encoded as per is_base64.',
                                     validate=marshmallow.validate.Length(min=1))
    description = marshmallow.fields.Str(required=True, description='Description of the attachment',
                                         validate=marshmallow.validate.Length(min=1))

    @marshmallow.post_load
    def make_attachment(self, data, **kwargs):
        return Attachment(data['is_base64'], data['content_type'], data['payload'])


@dataclasses.dataclass
class RequestBody:
    payload: str
    attachments: List[Attachment]


class RequestBodySchema(marshmallow.Schema):
    payload = marshmallow.fields.Str(required=True, description='Payload to send to Spine',
                                     validate=marshmallow.validate.Length(min=1))
    attachments = marshmallow.fields.Nested(AttachmentSchema, many=True, missing=[],
                                            description='Optional attachments to send with the payload. Only for use '
                                                        'for interactions that support sending attachments.')

    @marshmallow.post_load
    def make_request_body(self, data, **kwargs):
        return RequestBody(data['payload'], data['attachments'])
