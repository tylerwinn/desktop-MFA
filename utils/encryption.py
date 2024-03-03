from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class EncryptionHandler:
    def __init__(self, password=None, salt=None):
        if password is not None and salt is not None:
            self.key = self.derive_key(password, salt)
        else:
            self.key = self.generate_key()
        self.cipher_suite = Fernet(self.key)

    def derive_key(self, password, salt):
        """
        Derive a key using PBKDF2HMAC from the provided password and salt.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))  # Fernet key must be 32 url-safe base64-encoded bytes
        return key

    def encrypt(self, plaintext):
        """
        Encrypt the plaintext using the Fernet cipher suite.
        """
        encrypted_text = self.cipher_suite.encrypt(plaintext.encode())
        return encrypted_text

    def decrypt(self, encrypted_text):
        """
        Decrypt the encrypted text using the Fernet cipher suite.
        """
        decrypted_text = self.cipher_suite.decrypt(encrypted_text).decode()
        return decrypted_text