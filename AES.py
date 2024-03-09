from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import os

def derive_key(password, salt, key_size=32):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        iterations=100000,  # adjust as needed
        salt=salt,
        length=key_size
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

def aes_encrypt_message(message, password, salt):
    key = derive_key(password, salt)
    key_bytes = base64.urlsafe_b64decode(key)

    # Generate a random IV (Initialization Vector)
    iv = os.urandom(16)

    # Create an AES cipher object
    cipher = Cipher(algorithms.AES(key_bytes), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Encrypt the message
    ciphertext = encryptor.update(message) + encryptor.finalize()

    # Combine IV and ciphertext and encode in base64
    encrypted_message = base64.b64encode(iv + ciphertext).decode('utf-8')

    return encrypted_message

def aes_decrypt_message(encrypted_bytes, password, salt):
    key = derive_key(password, salt)
    key_bytes = base64.urlsafe_b64decode(key)

    # Decode base64 and extract IV
    # encrypted_bytes = base64.b64decode(encrypted_message)
    iv = encrypted_bytes[:16]

    # Create an AES cipher object
    cipher = Cipher(algorithms.AES(key_bytes), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Decrypt the message
    decrypted_message = decryptor.update(encrypted_bytes[16:]) + decryptor.finalize()

    return decrypted_message


if __name__ == '__main__':
    # Example usage
    email_content = "This is a confidential message."
    password = "your_secret_password"
    salt = os.urandom(16)  # Generate a random salt

    # Encrypt the email content
    encrypted_content = aes_encrypt_message(email_content, password, salt)
    print("Encrypted Content:", encrypted_content)

    # Decrypt the email content
    decrypted_content = aes_decrypt_message(encrypted_content, password, salt)
    print("Decrypted Content:", decrypted_content)
