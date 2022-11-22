from marshmallow import fields
from marshmallow.validate import Length
from marshmallow_enum import EnumField

from src import User
from src.views import BaseSchema


class UserSchema(BaseSchema):
    id = fields.UUID(dump_only=True)
    first_name = fields.Str(required=True, validate=Length(min=5, max=30))
    last_name = fields.Str(required=True, validate=Length(min=5, max=30))
    email = fields.Email(required=True, validate=Length(min=5, max=30))
    phone = fields.Str(required=True, validate=Length(min=5, max=30))
    city = fields.Str(required=True, validate=Length(min=5, max=30))
    status = EnumField(User.STATUSES, by_value=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class UserJWTSchema(UserSchema):
    access_token = fields.Str(dump_only=True)

class ResponseOneUserSchema(BaseSchema):
    data = fields.Nested("UserSchema", dump_only=True)
    message = fields.Str(dump_only=True)

class ResponseOneUserTokenSchema(BaseSchema):
    data = fields.Nested("UserJWTSchema", dump_only=True)
    message = fields.Str(dump_only=True)


create_user_schema = UserSchema()
response_one_user_schema = ResponseOneUserSchema()
response_one_user_token_schema = ResponseOneUserTokenSchema()

