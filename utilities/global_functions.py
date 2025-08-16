import uuid
from typing import Dict
import re
from utilities.exception import CustomAPIException

from datetime import datetime


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
            if value.lower() in ["true", "1"]:
                return True
            elif value.lower() in ["false", "0"]:
                return False
        raise CustomAPIException(f"Invalid boolean value.")
    except ValueError as exe:
        raise CustomAPIException(exe)

    except CustomAPIException as exe:
        raise CustomAPIException(exe)


def validate_phone_number(mobile_number: str, is_null: bool, /) -> str:
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



def validate_datetime(datetime_str):
    """
    Validates a datetime string and converts to a timezone-aware datetime object.
    Format: 'YYYY/MM/DD HH:MM' (24-hour format)
    """
    try:
        naive_dt = datetime.strptime(datetime_str, "%Y/%m/%d %H:%M")
        aware_dt = timezone.make_aware(naive_dt, timezone.get_current_timezone())
        return aware_dt
    except ValueError:
        raise CustomAPIException("Invalid datetime format. Use 'YYYY/MM/DD HH:MM'")


from django.utils import timezone

def validate_future_datetime(datetime_value, allow_null=True, allow_past=False, buffer_minutes=0):
    """
    Validates that a datetime is in the future.
    
    Args:
        datetime_value: The datetime object to validate
        allow_null (bool): Whether to allow None values (default: True)
        allow_past (bool): Whether to allow past datetimes (default: False)
        buffer_minutes (int): Minimum minutes into the future required (default: 0)
    
    Returns:
        datetime: The validated datetime object
        
    Raises:
        CustomAPIException: If validation fails
    """
    
    # Handle null values
    if datetime_value is None:
        if allow_null:
            return None
        else:
            raise CustomAPIException("Datetime value cannot be null.")
    
    # Ensure we have a datetime object
    if not isinstance(datetime_value, datetime):
        raise CustomAPIException("Invalid datetime format provided.")
    
    # Get current time for comparison
    now = timezone.now()
    
    # Add buffer time if specified
    if buffer_minutes > 0:
        from datetime import timedelta
        minimum_time = now + timedelta(minutes=buffer_minutes)
    else:
        minimum_time = now
    
    # Check if datetime is in the past (unless explicitly allowed)
    if not allow_past and datetime_value <= minimum_time:
        if buffer_minutes > 0:
            raise CustomAPIException(
                f"Datetime must be at least {buffer_minutes} minutes in the future."
            )
        else:
            raise CustomAPIException("Datetime must be in the future.")
    
    # Make sure datetime is timezone-aware
    if timezone.is_naive(datetime_value):
        # Convert naive datetime to timezone-aware using default timezone
        datetime_value = timezone.make_aware(datetime_value)
    
    return datetime_value