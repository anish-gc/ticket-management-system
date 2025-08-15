import uuid
from typing import Dict
import re
from utilities.exception import CustomAPIException


def generate_uuid():
    return uuid.uuid4().hex


def model_validation(
    model_name: object, error_msg: str, filter_query: Dict[str, any]
) -> any:
    try:
        if not model_name.objects.filter(**filter_query).exists():
            raise CustomAPIException(error_msg)

        return model_name.objects.get(**filter_query)

    except CustomAPIException as exe:
        raise CustomAPIException(exe.detail)

    except Exception as exe:
        raise Exception(exe)



def validate_boolean(value):
    try:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if value.lower() in ['true', '1']:
                return True
            elif value.lower() in ['false', '0']:
                return False
        raise CustomAPIException(f"Invalid boolean value.")
    except ValueError as exe:
        raise CustomAPIException(exe)
    
    except CustomAPIException as exe:
        raise CustomAPIException(exe)
    


def validate_phone_number(mobile_number:str, is_null:bool, /)->str:
    """
    Validate a mobile number based on specified criteria.
    - mobile_number (str): The mobile number to validate.
    - is_null (bool): Indicates whether a null or empty string should be considered valid.
    """
    if is_null and not mobile_number:
        return True
    else:
        if mobile_number is None or mobile_number == "":
            raise CustomAPIException("Mobile number cannot be blank.")
    
    if not mobile_number.isdigit():
        raise CustomAPIException("Mobile number must be digits only.")
    
    if len(mobile_number) != 10:    
        raise CustomAPIException("Mobile number must be exactly 10 digits long.")
    
    pattern = r"^(984|985|986|974|975|976|980|981|982|970|961|962|988)\d{7}$"
    if not re.match(pattern, mobile_number):
        raise CustomAPIException("Invalid mobile number pattern.")

    return True    


def validate_password(password, /):
    return True
    pattern = r"^(?=.*[A-Z])(?=.*[!@#$%^&*()])(?=.*\d).{8,}$"
    return bool(re.match(pattern, password))
