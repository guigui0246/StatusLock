from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

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
    return world.random.choice(ALL_FILLERS + ([MACGUFFIN_FILLER_ITEM_NAME] if world.options.macguffin_amount > 0 else []))


def create_item(world: SLWorld, name: str) -> SLItem:
    classification = DEFAULT_ITEM_CLASSIFICATIONS[name]

    if name == MACGUFFIN_ITEM_NAME and world.options.macguffin_amount > 0:
        classification = ItemClassification.progression_deprioritized_skip_balancing

    return SLItem(name, classification, ITEM_NAME_TO_ID[name], world.player)


def create_all_items(world: SLWorld) -> None:
    itempool: list[Item] = []

    # TODO: complete itempool based on options
    has_release_shards = world.options.release_shards_amount > 0

    if has_release_shards:
        itempool.extend([world.create_item("Release Shard")] * world.options.release_shards_amount)

    number_of_items = len(itempool)
    number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))
    needed_number_of_filler_items = number_of_unfilled_locations - number_of_items
    itempool += [world.create_filler() for _ in range(needed_number_of_filler_items)]
    world.multiworld.itempool += itempool
