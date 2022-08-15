import re

from django.core.exceptions import ValidationError


def validate_phone_number(phone_number):
    
    REGEX_PHONE_NUMBER = '^[a-zA-Z가-힣]+$'
    
    if not re.match(REGEX_PHONE_NUMBER,phone_number):
        raise ValidationError(message = "INVALID_PHONE_NUMBER")
  