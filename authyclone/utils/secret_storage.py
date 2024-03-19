import json
import os
from base64 import urlsafe_b64encode
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidSignature

class SecretStorage:
    def __init__(self, password, filename='secrets.json', salt_file='salt.key'):
        self.decrypted = False
        self.filename = filename
        self.salt_file = salt_file
        self.salt = self.load_or_generate_salt()
        self.key = self.derive_key(password, self.salt)
        self.secrets = {}
        self.load_secrets()
    

    def load_or_generate_salt(self):
        if os.path.exists(self.salt_file):
            with open(self.salt_file, 'rb') as file:
                salt = file.read()
        else:
            salt = os.urandom(16)
            with open(self.salt_file, 'wb') as file:
                file.write(salt)
        return salt

    def derive_key(self, password, salt):
        # Derive a secure key from the password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt_data(self, data):
        fernet = Fernet(self.key)
        return fernet.encrypt(data.encode())

    def decrypt_data(self, data):
        fernet = Fernet(self.key)
        try:
            return fernet.decrypt(data).decode()
        except Exception as e:
            print(e)
            raise ValueError("Invalid password or corrupted data")

    def load_secrets(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'rb') as file:
                encrypted_data = file.read()
                try:
                    decrypted_data = self.decrypt_data(encrypted_data)
                    self.secrets = json.loads(decrypted_data)
                    self.decrypted = True
                except ValueError:
                    print("Unable to decrypt the data. The password might be incorrect, or the data is corrupted.")

    def save_secret(self, name, secret):
        self.secrets[name] = secret
        encrypted_data = self.encrypt_data(json.dumps(self.secrets))
        with open(self.filename, 'wb') as file:
            file.write(encrypted_data)

    def get_secret(self, name):
        print(self.secrets.get(name))
        return self.secrets.get(name, None)

    def remove_secret(self, name):
        if name in self.secrets:
            del self.secrets[name]
            encrypted_data = self.encrypt_data(json.dumps(self.secrets))
            with open(self.filename, 'wb') as file:
                file.write(encrypted_data)