from django.utils.crypto import get_random_string
from django.conf import settings

def generate_security_code():
    """
    Returns a unique random `security_code` for given `TOKEN_LENGTH` in the settings.
    Default token length = 6
    """
    token_length = getattr(settings, "TOKEN_LENGTH", 6)
    return get_random_string(token_length, allowed_chars="0123456789")