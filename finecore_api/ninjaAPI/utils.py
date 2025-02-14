import secrets
import string


def generate_api_key(length=64):
    # Define the character set for the API key
    characters = string.ascii_letters + string.digits  # A-Z, a-z, 0-9

    # Generate a random string of the specified length
    api_key = ''.join(secrets.choice(characters) for _ in range(length))

    return api_key
