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

    # def _cmd_slot_data(self):
    #    """Show Slot Data, For Debug Purposes. Probably don't run this"""
    #    self.output(f"Data: {str(self.ctx.pairs)}")
    #    pass

    def _cmd_set_password(self, key: str = ""):
        """Sets the admin password"""
        self.ctx.admin_password = key
        self.output("Correctly set password")

    def _cmd_save(self):
        """Saves the current information (like passwords) to a file"""
        path = self.config_folder
        if not os.path.exists(path):
            os.makedirs(path)
        with open(self.config_file, 'wb') as f:
            pickle.dump(self.ctx.all_data, f)
        self.output("Saved current passwords and settings")

    def _cmd_load_keys(self):
        """Loads the player's previously saved information (like passwords) from a file"""
        with open(self.config_file, 'rb') as f:
            self.ctx.all_data = pickle.load(f)
        self.output("Loaded previous passwords and settings")
