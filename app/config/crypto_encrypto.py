import base64
from cryptography.fernet import Fernet, InvalidToken
from app.config.config import settings 
   
   
key = settings.key_crypto
cipher = Fernet(key)

def is_base64(s):
    try:
        return base64.b64encode(base64.b64decode(s)).decode('utf-8') == s
    except Exception:
        return False


async def async_decrypt(encoded_data: str):
    if not is_base64(encoded_data):
       
        return encoded_data  

    try:
        encrypted = base64.b64decode(encoded_data.encode('utf-8'))
        decrypted = cipher.decrypt(encrypted).decode('utf-8')
        return decrypted
    except InvalidToken:
        return None