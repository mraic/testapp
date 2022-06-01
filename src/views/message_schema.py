from marshmallow import Schema, fields


class MessageSchema(Schema):
    message = fields.String(dump_only=True)


message_response_schema = MessageSchema()
