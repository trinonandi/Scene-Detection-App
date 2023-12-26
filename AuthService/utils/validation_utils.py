import re

from email_validator import validate_email, EmailNotValidError


def is_valid_email(email: str):
    try:
        email_info = validate_email(email, check_deliverability=True)
        return True, email_info.normalized

    except EmailNotValidError as e:
        print(str(e))
        return False


def is_valid_password(password: str):
    pattern = re.compile(
        r'^(?=.*[a-z])'  # At least one lowercase letter
        r'(?=.*[A-Z])'  # At least one uppercase letter
        r'(?=.*\d)'  # At least one digit
        r'(?=.*[!@#$%^&*])'  # At least one special character
        r'.{8,}$'  # At least 8 characters in total
    )

    # Check if the password matches the pattern
    return bool(pattern.match(password))