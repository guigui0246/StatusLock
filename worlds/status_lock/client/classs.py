from enum import Enum, auto
from typing import Any
from .cryptography.fernet import Fernet


class SecurityLevel(Enum):
    Gettable = auto()
    Ungettable = auto()


class Data:
    __admin_encryption_key: bytes | None = None  # Will be replaced by a Fernet.generate_key()
    __SecurityLevel = SecurityLevel

    def __init__(self):
        self.__admin_password: str | None = None
        self.__security = Data.__SecurityLevel.Gettable

    @property
    def admin_encryption_key(cls):
        raise PermissionError("admin_encryption_key is write-only")

    @admin_encryption_key.setter
    def admin_encryption_key(cls, value: bytes) -> None:
        if Data.__admin_encryption_key is not None:
            raise PermissionError("admin_encryption_key can only be set once")
        Data.__admin_encryption_key = value

    @property
    def admin_password(self) -> str | None:
        if self.__admin_password is None:
            return None

        if Data.__admin_encryption_key is None:
            raise PermissionError("admin_encryption_key must be set before reading admin_password")

        if self.__security != Data.__SecurityLevel.Gettable:
            return self.__admin_password

        return Fernet(Data.__admin_encryption_key).decrypt(self.__admin_password.encode("utf-8")).decode("utf-8")

    @admin_password.setter
    def admin_password(self, value: str | None) -> None:
        if self.__security != Data.__SecurityLevel.Gettable:
            raise PermissionError("You are on a read-only instance")
        if value is None:
            self.__admin_password = None
            return

        if Data.__admin_encryption_key is None:
            raise PermissionError("admin_encryption_key must be set before setting admin_password")

        self.__admin_password = Fernet(Data.__admin_encryption_key).encrypt(value.encode("utf-8")).decode("utf-8")

    def read_only(self) -> "Data":
        d = Data()
        d.__admin_password = self.__admin_password
        d.__security = Data.__SecurityLevel.Ungettable
        return d

    def __str__(self) -> str:
        sl: list[str] = []
        if self.__security == Data.__SecurityLevel.Gettable:
            sl.append("Password security: decodable")
        else:
            sl.append("Password security: encoded")
        if self.__admin_password is not None:
            sl.append(f"Admin password: \"{self.admin_password}\"")
        return "(" + ";".join(sl) + ")"

    def __getstate__(self):
        if self.__security != Data.__SecurityLevel.Gettable:
            raise PermissionError("You are on a read-only instance")
        state = self.__dict__.copy()
        state.pop("__security", None)
        state.pop("__admin_encryption_key", None)
        state.pop("Data__security", None)
        state.pop("Data__admin_encryption_key", None)
        state.pop("_Data__security", None)
        state.pop("_Data__admin_encryption_key", None)
        return state

    def __setstate__(self, state: Any):
        refuse = False
        if not any(
            k in ["_Data__admin_password"] for k in state.keys()
        ):
            refuse = True
        if (
            getattr(
                self, '__security',
                # If we don't have __security yet then it's pickle and we should allow it
                # but if __admin_password is not in the state then it's someone trying to fake pickle
                # in the hope of getting the admin password, so we should refuse it
                None if refuse else Data.__SecurityLevel.Gettable
            ) != Data.__SecurityLevel.Gettable
        ):
            raise PermissionError("You are on a read-only instance")
        if refuse:
            raise ValueError("admin_password must be set in the state")
        self.__dict__.update(state)
        self.__security = Data.__SecurityLevel.Gettable


del SecurityLevel  # SecurityLevel should be kept in this file alone


class DataClass:
    def __init__(self):
        self.data: dict[tuple[str, tuple[str, ...]], Data] = {}

    def __getitem__(self, key: tuple[str, tuple[str, ...]]) -> Data:
        return self.data.setdefault(key, Data())


__all__ = ["Data", "DataClass"]
