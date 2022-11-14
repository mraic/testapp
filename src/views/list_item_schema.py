from marshmallow import fields

from src.views import BaseSchema


class ListItemSchema(BaseSchema):
    id = fields.UUID(dump_only=True)
    name = fields.Str(dump_only=True)


class ResponseManyListItemSchema(BaseSchema):
    data = fields.Nested("ListItemSchema", many=True, dump_only=True)
    message = fields.Str(dump_only=True)


list_item_schema = ListItemSchema()
response_many_li_schema = ResponseManyListItemSchema()
