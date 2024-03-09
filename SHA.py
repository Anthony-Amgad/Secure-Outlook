from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64

def hash_data(data):
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(data.encode('utf-8'))
    return digest.finalize()


if __name__ == '__main__':
    # Example Usage
    plaintext = "Hello, secure email communication!"

    # Hashing (SHA-256)
    hashed_data = hash_data(plaintext)

    # Base64 Encoding for display
    print("Plaintext:", plaintext.decode())
    print("Hashed Data:", base64.b64encode(hashed_data).decode())

