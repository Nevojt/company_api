import base64
from cryptography.fernet import Fernet, InvalidToken
from app.config.config import settings 
import secrets
   
key = settings.key_crypto
cipher = Fernet(key)

def is_base64(s):
    try:
        return base64.b64encode(base64.b64decode(s)).decode('utf-8') == s
    except Exception:
        return False

async def async_encrypt(data: str):
    if data is None:
        return None
    encrypted = cipher.encrypt(data.encode())
    encoded_string = base64.b64encode(encrypted).decode('utf-8')
    return encoded_string

async def async_decrypt(encoded_data: str):

    if not is_base64(encoded_data):
        return encoded_data

    try:
        encrypted = base64.b64decode(encoded_data.encode('utf-8'))
        decrypted = cipher.decrypt(encrypted).decode('utf-8')
        return decrypted
    except InvalidToken as e:
        return None


# Generate a key and instantiate a Fernet instance
cipher_suite = Fernet(key)
# Mail crypto token

async def generate_encrypted_token(email: str) -> str:
    """
    Generate an encrypted token containing the email.
    """
    # Encrypt the email
    encrypted_email = cipher_suite.encrypt(email.encode())
    # Generate a base token
    base_token = secrets.token_urlsafe()
    # Return the combined token
    return f"{base_token}.{encrypted_email.decode()}"


async def decrypt_token(token: str) -> str:
    """
    Decrypt the token to extract the email.
    """
    # Split the token to get the encrypted part
    base_token, encrypted_email = token.rsplit('.', 1)
    # Decrypt the email
    decrypted_email = cipher_suite.decrypt(encrypted_email.encode())
    return decrypted_email.decode()
