from __future__ import annotations
import os
import pickle

from CommonClient import ClientCommandProcessor
from .context import SLContext


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
        self.ctx.ui.show()

    def get_status_lock_lines(self) -> list[str]:
        """Get the lines you'd need to paste into the server"""
        # TODO: implement this
        return []

    def _cmd_copy_lines(self) -> None:
        """Copy the lines you'd need to paste into the clipboard"""
        import clipboard
        s = "\n".join(self.get_status_lock_lines())
        clipboard.copy(s)
        pass


__all__ = ["SLClientCommandProcessor"]
