from marshmallow import Schema
from . import Hellper


class BaseSchema(Schema):
    class Meta:
        datetimeformat = Hellper.datetime_format
        dateformat = Hellper.date_format
