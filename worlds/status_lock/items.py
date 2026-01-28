from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from BaseClasses import Item, ItemClassification
from worlds.status_lock.options import GoalType

if TYPE_CHECKING:
    from .world import SLWorld


MACGUFFIN_ITEM_NAME = "Macguffin"
MACGUFFIN_FILLER_ITEM_NAME = "Broken Macguffin"


ITEM_NAME_TO_ID = {
    "Release Shard": 1,  # progress
    "Auto-Release Shard": 2,  # progress
    "Collect Shard": 3,  # progress
    "Auto-Collect Shard": 4,  # progress
    "Mini Hint Crystal": 5,  # progress
    "Small Hint Crystal": 6,  # progress
    "Medium Hint Crystal": 7,  # progress
    "Big Hint Crystal": 8,  # progress
    "Giant Hint Crystal": 9,  # progress
    MACGUFFIN_ITEM_NAME: 10,  # potentially progression
    MACGUFFIN_FILLER_ITEM_NAME: 11,  # filler
    "Broken Crystal": 12,  # filler
    "0% Progress": 13,  # filler
    "> sl: Choo choo": 14,  # filler
    "Notification Trap": 15,  # traps
    "Hint Cost Trap": 16,  # traps
}

DEFAULT_ITEM_CLASSIFICATIONS = {
    "Release Shard": ItemClassification.progression | ItemClassification.useful,
    "Auto-Release Shard": ItemClassification.progression | ItemClassification.useful,
    "Collect Shard": ItemClassification.progression | ItemClassification.useful,
    "Auto-Collect Shard": ItemClassification.progression | ItemClassification.useful,
    "Mini Hint Crystal": ItemClassification.progression | ItemClassification.useful,
    "Small Hint Crystal": ItemClassification.progression | ItemClassification.useful,
    "Medium Hint Crystal": ItemClassification.progression | ItemClassification.useful,
    "Big Hint Crystal": ItemClassification.progression | ItemClassification.useful,
    "Giant Hint Crystal": ItemClassification.progression | ItemClassification.useful,
    MACGUFFIN_ITEM_NAME: ItemClassification.filler,
    MACGUFFIN_FILLER_ITEM_NAME: ItemClassification.filler,
    "Broken Crystal": ItemClassification.filler,
    "0% Progress": ItemClassification.filler,
    "> sl: Choo choo": ItemClassification.filler,
    "Notification Trap": ItemClassification.trap,
    "Hint Cost Trap": ItemClassification.trap,
}


ALL_TRAPS = [
    "Notification Trap",
    "Hint Cost Trap",
]


ALL_FILLERS = [
    # MACGUFFIN_FILLER_ITEM_NAME, # Commented out because it is only present if macguffins are enabled
    "Broken Crystal",
    "0% Progress",
    "> sl: Choo choo",
]


# TODO: make macguffin only present if macguffin goal is enabled
# replace "world.options.macguffin_amount > 0" by a rule


class SLItem(Item):
    game = "Status Lock"


def get_filler_item_name(world: SLWorld) -> str:
    if world.random.randint(0, 99) < world.options.trap_chance:
        return world.random.choice(ALL_TRAPS)
    return world.random.choice(ALL_FILLERS)


def create_item(world: SLWorld, name: str) -> SLItem:
    classification = DEFAULT_ITEM_CLASSIFICATIONS[name]

    if name == MACGUFFIN_ITEM_NAME and world.options.macguffin_amount > 0:
        classification = ItemClassification.progression_deprioritized_skip_balancing

    return SLItem(name, classification, ITEM_NAME_TO_ID[name], world.player)


def create_all_items(world: SLWorld) -> None:
    itempool: list[Item] = []
    slot_data = getattr(world.multiworld, "slot_data", None)
    if slot_data is None:
        world.multiworld.slot_data: dict[int, Any] = {}  # type: ignore
    world.multiworld.slot_data.setdefault(world.player, {})  # type: ignore

    has_release_shards = world.options.release_shards_amount > 0
    if has_release_shards:
        itempool.extend([world.create_item("Release Shard")] * world.options.release_shards_amount)
        world.multiworld.slot_data[world.player]["has_release_shards"] = True  # type: ignore

    has_auto_release_shards = world.options.auto_release_shards_amount > 0
    if has_auto_release_shards:
        itempool.extend([world.create_item("Auto-Release Shard")] * world.options.auto_release_shards_amount)
        world.multiworld.slot_data[world.player]["has_auto_release_shards"] = True  # type: ignore

    has_collect_shards = world.options.collect_shards_amount > 0
    if has_collect_shards:
        itempool.extend([world.create_item("Collect Shard")] * world.options.collect_shards_amount)
        world.multiworld.slot_data[world.player]["has_collect_shards"] = True  # type: ignore

    has_auto_collect_shards = world.options.auto_collect_shards_amount > 0
    if has_auto_collect_shards:
        itempool.extend([world.create_item("Auto-Collect Shard")] * world.options.auto_collect_shards_amount)
        world.multiworld.slot_data[world.player]["has_auto_collect_shards"] = True  # type: ignore

    has_macguffins = (
        world.options.macguffin_amount > 0
        and bool(cast(GoalType, world.options.goal_choice.value) & GoalType.macguffin_collection)
    )
    if has_macguffins:
        itempool.extend([world.create_item(MACGUFFIN_ITEM_NAME)] * world.options.macguffin_amount)
        world.multiworld.slot_data[world.player]["has_macguffins"] = True  # type: ignore

    has_hint_crystals = (
        world.options.crystal_amount > 0
        and world.options.max_hint_cost > world.options.min_hint_cost
    )
    if has_hint_crystals:
        amount = world.options.crystal_amount
        crystal_types: dict[int, str] = {
            0: "Mini Hint Crystal",
            1: "Small Hint Crystal",
            5: "Medium Hint Crystal",
            20: "Big Hint Crystal",
            80: "Giant Hint Crystal",
        }
        decomp: dict[int, int] = {1: 0, 5: 1, 20: 5, 80: 20}
        crystals_values: list[int] = [80] if amount % 2 else [20, 80]
        amount -= 2
        while amount > 0 and any(crystals_values):  # any will return false if we only have 0 in the list
            value = world.random.choice(crystals_values)
            if value in decomp:
                crystals_values.remove(value)
                crystals_values.extend([decomp[value]] * 3)
                amount -= 2
        crystals_values.extend([0] * amount)  # Fill the rest with mini crystals
        itempool.extend([world.create_item(crystal_types[v]) for v in crystals_values])
        world.multiworld.slot_data[world.player]["has_hint_crystals"] = True  # type: ignore
        world.multiworld.slot_data[world.player]["max_hint_cost"] = world.options.max_hint_cost  # type: ignore
        world.multiworld.slot_data[world.player]["min_hint_cost"] = world.options.min_hint_cost  # type: ignore

    number_of_items = len(itempool)
    number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))
    needed_number_of_filler_items = number_of_unfilled_locations - number_of_items
    itempool += [world.create_filler() for _ in range(needed_number_of_filler_items)]
    world.multiworld.itempool += itempool
