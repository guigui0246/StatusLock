from __future__ import annotations

from worlds.status_lock.items import OnlineData, MACGUFFIN_ITEM_NAME
from worlds.status_lock.locations import LOCATION_NAME_TO_ID
from worlds.status_lock.options import GoalType
from .cryptography.fernet import Fernet
import os
import sys
import asyncio
from typing import Any

from kivy.core.window import Window
from NetUtils import ClientStatus, Endpoint

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
        self.item_update_task: asyncio.Task[None] | None = None
        self.running_item_update_task: asyncio.Task[None] | None = None
        self.waiting_item_update_task: asyncio.Task[None] | None = None
        self.item_update_task_lock: asyncio.Lock = asyncio.Lock()
        self.item_update_task_lock2: asyncio.Lock = asyncio.Lock()
        self.send_index: int = 0
        self.all_data = DataClass()
        self.command_processor_instance: SLClientCommandProcessor | None = None

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
            self.item_update_task = asyncio.create_task(self.item_update())

        if cmd in {"ReceivedItems"}:
            self.item_update_task = asyncio.create_task(self.item_update())

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

    async def item_update(self):
        if self.slot_data is None:
            return
        if self.item_update_task_lock2.locked():  # Already 1 queued
            return
        await self.item_update_task_lock2.acquire()
        self.waiting_item_update_task = asyncio.current_task()  # Prevents losing the task and getting a lock
        await self.item_update_task_lock.acquire()  # Wait for previous to finish before running the queued one
        self.running_item_update_task = asyncio.current_task()  # Prevents losing the task and getting a lock
        self.item_update_task_lock2.release()

        try:
            items = [self.item_names.lookup_in_game(i.item) for i in self.items_received]
            max_id = len(items)
            await self.check_locations(list(v for v in LOCATION_NAME_TO_ID.values() if v <= max_id))

            goal = self.slot_data.get("goal_choice", 0)
            goal_conditions = {
                "release_shards": goal & GoalType.release_shards,
                "auto_release_shards": goal & GoalType.auto_release_shards,
                "collect_shards": goal & GoalType.collect_shards,
                "auto_collect_shards": goal & GoalType.auto_collect_shards,
                "giant_crystal": goal & GoalType.giant_crystal,
                "filler_completion": goal & GoalType.filler_completion,
                "macguffin_collection": goal & GoalType.macguffin_collection,
            }
            goal_fullfilled_conditions = {
                "release_shards": True,
                "auto_release_shards": True,
                "collect_shards": True,
                "auto_collect_shards": True,
                "giant_crystal": True,
                "filler_completion": True,
                "macguffin_collection": True,
            }
            if self.slot_data.get("has_release_shards", False):
                goal_fullfilled_conditions["release_shards"] = (
                    self.slot_data.get("release_shards_needed_amount", 0) <= items.count("Release Shard")
                )
            if self.slot_data.get("has_auto_release_shards", False):
                goal_fullfilled_conditions["auto_release_shards"] = (
                    self.slot_data.get("auto_release_shards_needed_amount", 0) <= items.count("Auto-Release Shard")
                )
            if self.slot_data.get("has_collect_shards", False):
                goal_fullfilled_conditions["collect_shards"] = (
                    self.slot_data.get("collect_shards_needed_amount", 0) <= items.count("Collect Shard")
                )
            if self.slot_data.get("has_auto_collect_shards", False):
                goal_fullfilled_conditions["auto_collect_shards"] = (
                    self.slot_data.get("auto_collect_shards_needed_amount", 0) <= items.count("Auto-Collect Shard")
                )
            if self.slot_data.get("has_macguffins", False):
                goal_fullfilled_conditions["macguffin_collection"] = (
                    self.slot_data.get("macguffins_needed_amount", 0) <= items.count(MACGUFFIN_ITEM_NAME)
                )

            if self.slot_data.get("has_hint_crystals", False):
                crystal_types_order: list[str] = [
                    "Mini Hint Crystal",
                    "Small Hint Crystal",
                    "Medium Hint Crystal",
                    "Big Hint Crystal",
                    "Giant Hint Crystal"
                ]
                combined = list(filter(lambda x: x in crystal_types_order, items))

                for i, name in enumerate(crystal_types_order):
                    if i >= len(crystal_types_order) - 1:
                        break
                    if name not in combined:
                        continue
                    amount = len(list(filter(lambda x: x == name, combined)))
                    if amount < 3:
                        continue
                    combine, left = divmod(amount, 3)
                    for _ in range(amount):
                        combined.remove(name)
                    combined += [name] * left
                    combined += [crystal_types_order[i + 1]] * combine
                goal_fullfilled_conditions["giant_crystal"] = crystal_types_order[-1] in combined

            goal_fullfilled = all(goal_fullfilled_conditions[cond] for cond in goal_conditions if goal_conditions[cond])
            if goal_fullfilled:
                await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
                self.finished_game = True

            # todo: admin changes

        finally:
            self.item_update_task_lock.release()


__all__ = ["SLContext"]
