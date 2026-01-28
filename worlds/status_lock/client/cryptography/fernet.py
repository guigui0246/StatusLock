import base64
import secrets


class Fernet:
    def __init__(self, key: bytes):
        if len(key) == 0:
            raise ValueError("Key must not be empty")
        self.key = key

    def encrypt(self, password: bytes) -> bytes:
        mixed = bytes(a ^ self.key[i % len(self.key)] for i, a in enumerate(password))
        return base64.b64encode(mixed)

    def decrypt(self, token: bytes) -> bytes:
        try:
            mixed = base64.b64decode(token)
        except Exception as e:
            raise ValueError("Invalid token") from e

        password = bytes(a ^ self.key[i % len(self.key)] for i, a in enumerate(mixed))
        return password

    @staticmethod
    def generate_key() -> bytes:
        return secrets.token_bytes(32)
