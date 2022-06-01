from marshmallow import Schema, fields, validate, pre_load


class OperatorSchema(Schema):
    value = fields.Str(
        required=True,
        allow_none=True,
        metadata={'description': 'Vrijednost za pretragu'})
    operator = fields.Str(
        required=True,
        validate=validate.OneOf(["CONTAINS", "START", "EXACT", "FINISH"]),
        metadata={
            'description': 'Način na koji će se izvršiti pretraga vrijednosti'})

    @pre_load
    def pre_load_data(self, data, **kwargs):
        if not data.get('value', None):
            data['value'] = None
        return data


class PaginationSchema(Schema):
    start = fields.Int(
        required=True,
        metadata={
            'description': "Broj stranice za koju će se prikazat rezultati"})
    length = fields.Int(
        required=True,
        metadata={'description': "Broj redaka po stranici"})
