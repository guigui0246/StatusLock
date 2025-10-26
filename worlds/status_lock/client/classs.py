from cryptography.fernet import Fernet


class Data:
    _admin_encryption_key: bytes | None = None  # Will be replaced by a Fernet.generate_key()

    def __init__(self):
        self._admin_password: str | None = None

    @property
    def admin_encryption_key(cls):
        raise PermissionError("admin_encryption_key is write-only")

    @admin_encryption_key.setter
    def admin_encryption_key(cls, value: bytes) -> None:
        if Data._admin_encryption_key is not None:
            raise PermissionError("admin_encryption_key can only be set once")
        Data._admin_encryption_key = value

    @property
    def admin_password(self) -> str | None:
        if self._admin_password is None:
            return None

        if Data._admin_encryption_key is None:
            raise PermissionError("admin_encryption_key must be set before reading admin_password")

        return Fernet(Data._admin_encryption_key).decrypt(self._admin_password.encode("utf-8")).decode("utf-8")

    @admin_password.setter
    def admin_password(self, value: str | None) -> None:
        if value is None:
            self._admin_password = None
            return

        if Data._admin_encryption_key is None:
            raise PermissionError("admin_encryption_key must be set before setting admin_password")

        self._admin_password = Fernet(Data._admin_encryption_key).encrypt(value.encode("utf-8")).decode("utf-8")


class DataClass:
    def __init__(self):
        self.data: dict[tuple[str, tuple[str, ...]], Data] = {}

    def __getitem__(self, key: tuple[str, tuple[str, ...]]) -> Data:
        return self.data.setdefault(key, Data())
