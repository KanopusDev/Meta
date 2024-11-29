
import phonenumbers
from typing import Tuple

def validate_phone_number(phone: str) -> Tuple[bool, str]:
    try:
        number = phonenumbers.parse(phone)
        if phonenumbers.is_valid_number(number):
            # Format to E.164 format
            formatted = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
            return True, formatted
        return False, "Invalid phone number"
    except Exception as e:
        return False, str(e)