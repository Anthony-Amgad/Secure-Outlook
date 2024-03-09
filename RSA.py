from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
import base64
from SHA import hash_data

def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key

def rsa_pubserialize(public_key):
    serialized_public_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return serialized_public_key

def rsa_privserialize(private_key):
    serialized_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    return serialized_private_key

def rsa_pubencrypt_data(data, serialized_public_key):

    # Load the serialized public key
    loaded_public_key = serialization.load_pem_public_key(
        serialized_public_key,
        backend=default_backend()
    )

    # Encrypt the data
    ciphertext = loaded_public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return ciphertext

def rsa_privdecrypt_data(ciphertext, serialized_private_key):

    loaded_private_key = serialization.load_pem_private_key(
        serialized_private_key,
        password=None,
        backend=default_backend()
    )

    # Decrypt the data
    decrypted_data = loaded_private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return decrypted_data

def sign_message(plaintext, serialized_private_key):

    loaded_private_key = serialization.load_pem_private_key(
        serialized_private_key,
        password=None,
        backend=default_backend()
    )

    hashed = hash_data(plaintext)

    signature = loaded_private_key.sign(
        hashed,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def verify_signature(plaintext, signature, serialized_public_key):

    loaded_public_key = serialization.load_pem_public_key(
        serialized_public_key,
        backend=default_backend()
    )

    hashed = hash_data(plaintext)

    try:
        loaded_public_key.verify(
            signature,
            hashed,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        # print("Verification Valid!")
        return True
    except:
        # print("Verification Failed")
        return False
    
if __name__ == '__main__':
    # Example Usage
    private_key, public_key = generate_key_pair()
    plaintext = b"Hello, secure email communication!"


    # Hashing (SHA-256)
    hashed_data = hash_data(plaintext)

    # Pub Encrypt
    encr = rsa_pubencrypt_data(plaintext, rsa_pubserialize(public_key))
    print("Encrypted with Public:", encr)
    print("Decrypted with Private:", rsa_privdecrypt_data(encr, rsa_privserialize(private_key)))


    # Digital Signature
    signature = sign_message(plaintext, rsa_privserialize(private_key))
    verify_signature(plaintext, signature, rsa_pubserialize(public_key))

    # Base64 Encoding for display
    print("Plaintext:", plaintext.decode())
    print("Hashed Data:", base64.b64encode(hashed_data).decode())
    print("Signature:", base64.b64encode(signature).decode())
