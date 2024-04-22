import pyotp
from utils.secret_storage import SecretStorage

class TokenManager:
    def __init__(self, password):
        self.storage = SecretStorage(password)
        self.generators = {}
        for name, secret in self.storage.secrets.items():
            self.add_secret(name, secret)

    def add_secret(self, name, secret=None):
        secret = secret or TokenGenerator.generate_secret()
        self.generators[name] = TokenGenerator(secret)
        self.storage.save_secret(name, secret)

    def generate_token(self, name):
        if name in self.generators:
            return self.generators[name].generate_token()
        else:
            raise ValueError(f"No secret found for {name}")

    def remove_secret(self, name):
        if name in self.generators:
            del self.generators[name]
            self.storage.remove_secret(name)
        else:
            raise ValueError(f"No secret found for {name}")
        
    def get_accounts(self):
        return list(self.generators.keys())

class TokenGenerator:
    def __init__(self, secret=None):
        self.secret = secret or self.generate_secret()
        
    def generate_token(self):
        totp = pyotp.TOTP(self.secret)
        return totp.now()  # Returns a 6 digit token

    @staticmethod
    def generate_secret():
        return pyotp.random_base32()  # Generates a new secret key
