from __future__ import annotations

from worlds.status_lock.items import OnlineData
from .cryptography.fernet import Fernet
import os
import sys
import asyncio
from typing import Any

from kivy.core.window import Window
from NetUtils import Endpoint

from CommonClient import CommonContext
from .classs import Data, DataClass
from .commands import SLClientCommandProcessor


class SLContext(CommonContext):
    command_processor = SLClientCommandProcessor
    game = "Status Lock"
    items_handling = 0b111  # full remote apparently
    want_slot_data = True
    slot_data: OnlineData | None = None

    def __init__(self, server_address: str, password: str):
        super().__init__(server_address, password)
        self.send_index: int = 0
        self.all_data = DataClass()

        SL_FOLDER = ".StatusLockArchipelago"

        if "localappdata" in os.environ:
            self.save_path = os.path.expandvars(fr"%localappdata%/{SL_FOLDER}")
        else:
            self.save_path = os.path.expanduser(f"~/{SL_FOLDER}")

        if not self.save_path:
            sys.exit("Could not determine game communication path.")

        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        if not os.path.exists(os.path.join(self.save_path, "key")):
            with open(os.path.join(self.save_path, "key"), "wb") as f:
                key = Fernet.generate_key()
                f.write(key)
        else:
            with open(os.path.join(self.save_path, "key"), "rb") as f:
                key = f.read()

        Data.admin_encryption_key = key

    @property
    def admin_password(self) -> str | None:
        if self.auth is None or not self.player_names:
            return None
        return self.all_data[self.auth, tuple(self.player_names.values())].admin_password

    @admin_password.setter
    def admin_password(self, value: str | None) -> None:
        if self.auth is None or not self.player_names:
            return None
        self.all_data[self.auth, tuple(self.player_names.values())].admin_password = value

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    async def connection_closed(self):
        await super().connection_closed()

    @property
    def endpoints(self) -> list[Endpoint]:
        if self.server:
            return [self.server]
        else:
            return []

    async def shutdown(self):
        await super().shutdown()

    def on_package(self, cmd: str, args: dict[str, Any]) -> None:
        if cmd in {"Connected"}:
            print(args)
            slot_data = args.get('slot_data', None)
            if slot_data:
                self.slot_data = OnlineData(slot_data)
            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)

    def run_gui(self):
        """Import kivy UI system and start running it as self.ui_task."""
        from kvui import GameManager

        class SLManager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago")
            ]
            base_title = "Archipelago Status Lock Client"

            def hide(self) -> None:
                Window.hide()  # type: ignore

            def show(self) -> None:
                Window.show()  # type: ignore

        self.ui: SLManager = SLManager(self)  # type: ignore[reportIncompatibleVariableOverride]
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")


__all__ = ["SLContext"]
