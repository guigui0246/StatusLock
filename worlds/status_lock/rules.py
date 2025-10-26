from typing import TYPE_CHECKING

from BaseClasses import CollectionState
from worlds.generic.Rules import set_rule
from .items import ITEM_NAME_TO_ID
from .locations import LOCATION_NAME_PREFIX

if TYPE_CHECKING:
    from .world import SLWorld


def set_all_rules(world: SLWorld) -> None:
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)


def set_all_entrance_rules(world: SLWorld) -> None:
    # No entrance no rules
    pass


def create_count_items_function(number: int, world: SLWorld):
    def count_items(state: CollectionState) -> bool:
        total_items = 0
        for item_name in ITEM_NAME_TO_ID.keys():
            total_items += state.count(item_name, world.player)
        return total_items >= number
    return count_items


def set_all_location_rules(world: SLWorld) -> None:
    amount_locations = 0  # TODO: set
    for i in range(1, amount_locations):
        location = world.get_location(LOCATION_NAME_PREFIX + str(i))
        set_rule(location, create_count_items_function(i, world))


def set_completion_condition(world: SLWorld) -> None:
    world.multiworld.completion_condition[world.player] = lambda state: state.has("Victory", world.player)
