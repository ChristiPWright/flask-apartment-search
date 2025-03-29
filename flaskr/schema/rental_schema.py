from enum import Enum
from marshmallow import Schema, fields

class RentalStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class BaseRentalsSchema(Schema):
    rental_id = fields.UUID()
    lister_id = fields.UUID()
    title = fields.Str()
    description = fields.Str()
    address = fields.Str(required=True) #TODO: add a 3rd party for valid USPS address validation later
    price = fields.Decimal()
    status = fields.Enum(RentalStatus)

class CreateRentalSchema(BaseRentalsSchema):
    price = fields.Decimal(required=True)
    address = fields.Str(required=True)

class UpdateRentalSchema(BaseRentalsSchema):
    pass  

create_rental_schema = CreateRentalSchema()
update_rental_schema = UpdateRentalSchema()