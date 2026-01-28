from __future__ import annotations
import os
import platform
import subprocess
import pickle
from typing import TYPE_CHECKING

from CommonClient import ClientCommandProcessor
from .strings import CLIENT_PREFIX, CONNECT_ADMIN, HINT_COST, WEBSITE_PREFIX

if TYPE_CHECKING:
    from .context import SLContext


def copy_to_clipboard(text: str) -> None:
    system = platform.system()

    if system == "Windows":
        # Windows
        cmd = f'echo {text.strip()}| clip'
        os.system(cmd)

    elif system == "Darwin":
        # macOS
        process = subprocess.Popen(
            'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
        process.communicate(text.encode('utf-8'))

    elif system == "Linux":
        # Linux (requires xclip or xsel installed)
        try:
            process = subprocess.Popen(
                ['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
        except FileNotFoundError:
            try:
                process = subprocess.Popen(
                    ['xsel', '--clipboard', '--input'], stdin=subprocess.PIPE)
                process.communicate(text.encode('utf-8'))
            except FileNotFoundError:
                raise Exception(
                    "Install xclip or xsel to use clipboard functionality on Linux")

    else:
        raise Exception(f"Unsupported OS: {system}")


class SLClientCommandProcessor(ClientCommandProcessor):
    def __init__(self, ctx: SLContext):
        super().__init__(ctx)
        self.ctx = ctx
        self.config_folder = os.path.join(self.ctx.game_communication_path, 'config')
        self.config_file = os.path.join(self.config_folder, 'config')
        self.icon = None

    def _cmd_slot_data(self) -> None:
        """Show Slot Data, For Debug Purposes. Probably don't run this"""
        self.output(f"Data: {str(self.ctx.slot_data)}")

    def _cmd_set_password(self, key: str | None = None) -> None:
        """Sets the admin password"""
        self.ctx.admin_password = key
        self.output("Correctly set password")

    def _cmd_save(self) -> None:
        """Saves the current information (like passwords) to a file"""
        path = self.config_folder
        if not os.path.exists(path):
            os.makedirs(path)
        with open(self.config_file, 'wb') as f:
            pickle.dump(self.ctx.all_data, f)
        self.output("Saved current passwords and settings")

    def _cmd_load_keys(self) -> None:
        """Loads the player's previously saved information (like passwords) from a file"""
        with open(self.config_file, 'rb') as f:
            self.ctx.all_data = pickle.load(f)
        self.output("Loaded previous passwords and settings")

    def _cmd_tray(self) -> None:
        """Sends the client to a tray icon"""
        import pystray
        items: list[pystray.MenuItem] = [
            pystray.MenuItem("Open client", self.untray),
            pystray.MenuItem("Copy lines to paste", self._cmd_copy_lines),
        ]
        menu = pystray.Menu(items)
        self.icon = pystray.Icon("Status Lock", None, None, menu)
        self.icon.run_detached()
        self.ctx.ui.hide()

    def untray(self) -> None:
        """Go back from a tray icon to the client"""
        if self.icon is not None:
            self.icon.stop()
            del self.icon
            self.icon = None
        self.ctx.ui.show()

    def get_status_lock_lines(self, client: bool = False) -> list[str]:
        """Get the lines you'd need to paste into the server"""
        if self.ctx.slot_data is None:
            raise RuntimeError("No slot data available, please connect to a server first")
        l: list[str] = []
        changed = False
        if client:
            prefix = CLIENT_PREFIX
            l.append(prefix + CONNECT_ADMIN.format(password=self.ctx.admin_password))
        else:
            prefix = WEBSITE_PREFIX
        has_hint_crystals = self.ctx.slot_data["has_hint_crystals"]
        if has_hint_crystals:
            hint_cost = self.ctx.hint_cost if self.ctx.hint_cost is not None else 0
            crystal_types: dict[str, int] = {
                "Mini Hint Crystal": 0,
                "Small Hint Crystal": 1,
                "Medium Hint Crystal": 5,
                "Big Hint Crystal": 20,
                "Giant Hint Crystal": 80,
            }
            wanted_hint_cost: int = 0

            for i in self.ctx.items_received:
                name = self.ctx.item_names.lookup_in_game(i.item)
                if name in crystal_types:
                    wanted_hint_cost += crystal_types[name]

            wanted_hint_cost = min(wanted_hint_cost, 100)
            range: int = self.ctx.slot_data["max_hint_cost"] - self.ctx.slot_data["min_hint_cost"]
            wanted_hint_cost *= range // 100
            wanted_hint_cost += self.ctx.slot_data["min_hint_cost"]
            wanted_hint_cost = min(wanted_hint_cost, self.ctx.slot_data["max_hint_cost"])
            if hint_cost != wanted_hint_cost:
                l.append(prefix + HINT_COST.format(cost=wanted_hint_cost))
                changed = True
        # TODO: add release/collect/auto release/auto collect lines when they change
        if not changed:
            return []
        return l

    def _cmd_copy_lines(self) -> None:
        """Copy the lines you'd need to paste into the clipboard"""

        s = "\n".join(self.get_status_lock_lines())
        copy_to_clipboard(s)
        pass


__all__ = ["SLClientCommandProcessor"]
