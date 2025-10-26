from collections.abc import Mapping
from typing import Any
from worlds.AutoWorld import World
from . import items, locations, options, regions, rules, web_world


class SLWorld(World):
    """
    Status Lock is a meta-game where you need to collect varius crystals to unlock statuses
    """
    game = "Status Lock"

    web = web_world.SLWebWorld()

    options_dataclass = options.SLOptions
    options: options.SLOptions  # type: ignore[reportIncompatibleVariableOverride]

    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID

    origin_region_name = "Admin Panel"

    def create_regions(self) -> None:
        regions.create_and_connect_regions(self)
        locations.create_all_locations(self)

    def set_rules(self) -> None:
        rules.set_all_rules(self)

    def create_items(self) -> None:
        items.create_all_items(self)

    def create_item(self, name: str) -> items.SLItem:
        return items.create_item(self, name)

    def get_filler_item_name(self) -> str:
        return items.get_filler_item_name(self)

    def fill_slot_data(self) -> Mapping[str, Any]:
        return self.options.as_dict(
            *options.ALL_OPTIONS
        )
