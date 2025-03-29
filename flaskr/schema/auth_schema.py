from marshmallow import Schema, fields, validates

from flaskr.schema.schema_utils import validate_phone

class AuthSchema(Schema):
    email = fields.Email(required=True,  error_messages={"error": "Email is requred."})
    password = fields.Str(required=True,  error_messages={"error": "Password is required."})

class ProfileSchema(Schema):
    phone = fields.Str()
    name = fields.Str()

    @validates('phone')
    def phone_validator(self, value):
        validate_phone(value)
