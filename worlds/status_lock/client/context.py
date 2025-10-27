from __future__ import annotations
from cryptography.fernet import Fernet
import os
import sys
import asyncio
import shutil
from typing import Any
from NetUtils import Endpoint
import Utils

from CommonClient import logger, CommonContext
from .classs import Data, DataClass
from .commands import SLClientCommandProcessor


class SLContext(CommonContext):
    command_processor = SLClientCommandProcessor
    game = "Status Lock"
    items_handling = 0b111  # full remote
    want_slot_data = True

    def __init__(self, server_address: str, password: str):
        super(SLContext, self).__init__(server_address, password)
        self.send_index: int = 0
        self.all_data = DataClass()

        #############################################
        #  This is extracted from the osu apworld:  #
        # The only changed thing is the last folder #
        #############################################
        SL_FOLDER = ".StatusLockArchipelago"

        # self.game_communication_path: files go in this path to pass data between us and the actual game
        if "localappdata" in os.environ:
            self.game_communication_path = os.path.expandvars(fr"%localappdata%/{SL_FOLDER}")
        else:
            # not windows. game is an exe so let's see if wine might be around to run it
            if "WINEPREFIX" in os.environ:
                wineprefix = os.environ["WINEPREFIX"]
            elif shutil.which("wine") or shutil.which("wine-stable"):
                wineprefix = os.path.expanduser(
                    "~/.wine")  # default root of wine system data, deep in which is app data
            else:
                msg = "SLClient couldn't detect system type. Unable to infer required game_communication_path"
                logger.error("Error: " + msg)
                Utils.messagebox("Error", msg, error=True)
                sys.exit(1)
            self.game_communication_path = os.path.join(
                wineprefix,
                "drive_c",
                os.path.expandvars(f"users/$USER/Local Settings/Application Data/{SL_FOLDER}"))

        #############################################
        #  This was extracted from the osu apworld  #
        #############################################

        if not self.game_communication_path:
            sys.exit("Could not determine game communication path.")

        if not os.path.exists(self.game_communication_path):
            os.makedirs(self.game_communication_path)
        if not os.path.exists(os.path.join(self.game_communication_path, "key")):
            with open(os.path.join(self.game_communication_path, "key"), "wb") as f:
                key = Fernet.generate_key()
                f.write(key)
        else:
            with open(os.path.join(self.game_communication_path, "key"), "rb") as f:
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
            await super(SLContext, self).server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    async def connection_closed(self):
        await super(SLContext, self).connection_closed()
        for root, _, files in os.walk(self.game_communication_path):
            for file in files:
                if file.find("obtain") <= -1:
                    os.remove(root + "/" + file)

    @property
    def endpoints(self) -> list[Endpoint]:
        if self.server:
            return [self.server]
        else:
            return []

    async def shutdown(self):
        await super(SLContext, self).shutdown()
        for root, _, files in os.walk(self.game_communication_path):
            for file in files:
                if file.find("obtain") <= -1:
                    os.remove(root + "/" + file)

    def on_package(self, cmd: str, args: dict[str, Any]) -> None:
        if cmd in {"Connected"}:
            print(args)
            slot_data = args.get('slot_data', None)
            if slot_data:
                # TODO: process slot data
                pass
            if not os.path.exists(self.game_communication_path):
                os.makedirs(self.game_communication_path)

    def run_gui(self):
        """Import kivy UI system and start running it as self.ui_task."""
        from kvui import GameManager

        class SLManager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago")
            ]
            base_title = "Archipelago Status Lock Client"

            def hide(self) -> None:
                # TODO: withdraw window
                pass

            def show(self) -> None:
                # TODO: show window
                pass

        self.ui: SLManager = SLManager(self)  # type: ignore[reportIncompatibleVariableOverride]
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")

    @property
    def slot_data(self) -> Data | None:
        if self.auth is None:
            return None
        return self.all_data[self.auth, tuple(self.player_names.values())].read_only()


__all__ = ["SLContext"]
