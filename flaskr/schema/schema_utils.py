import re
from marshmallow import ValidationError

#TODO: allow for all valid phone format and sub value for singular valid international phone format
#   TODO: also consider libraries like https://pypi.org/project/phonenumbers/

# PHONE_REGEX = re.compile(r'^(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$') 
PHONE_REGEX = re.compile(r'^\(\d{3}\)\s\d{3}-\d{4}$')

def validate_phone(value: str):
    if not PHONE_REGEX.match(value):
        # raise ValidationError("Invalid phone number format. Expected 10–15 digits, optionally prefixed with +1.")
        raise ValidationError("Invalid phone number format. Only allowable format is (xxx) xxx-xxxx")