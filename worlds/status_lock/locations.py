from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Location, LocationProgressType
from rule_builder.rules import And, Rule, Has
from worlds.status_lock.options import GoalType

from . import items

if TYPE_CHECKING:
    from .world import SLWorld


LOCATION_NAME_PREFIX = "Location "


LOCATION_NAME_TO_ID = {
    f"{LOCATION_NAME_PREFIX}{i}": i for i in range(1, 3001)
    # we put 3000 because we need to account with the possible up to 1000 mcguffins + 1000 crystals + 100 each other items
}


class SLLocation(Location):
    game = "SL"
    progress_type = LocationProgressType.EXCLUDED


def create_all_locations(world: SLWorld) -> None:
    create_regular_locations(world)
    create_events(world)


def create_regular_locations(world: SLWorld) -> None:
    region = world.get_region("Admin Panel")

    locations = {k: v for k, v in LOCATION_NAME_TO_ID.items() if v <= len(items.create_item_pool(world))}

    region.add_locations(
        locations,
        location_type=SLLocation,
    )


def makeHas(args: tuple[str, int]) -> Rule[SLWorld]:
    return Has(*args)


def make_goal_from_item_pool(world: SLWorld) -> Rule[SLWorld]:
    items_pool = list(item.name for item in items.create_item_pool(world))
    goal = world.options.goal_choice
    goal_conditions = {
        "release_shards": goal & GoalType.release_shards,
        "auto_release_shards": goal & GoalType.auto_release_shards,
        "collect_shards": goal & GoalType.collect_shards,
        "auto_collect_shards": goal & GoalType.auto_collect_shards,
        "giant_crystal": goal & GoalType.giant_crystal,
        "filler_completion": goal & GoalType.filler_completion,
        "macguffin_collection": goal & GoalType.macguffin_collection,
    }
    goal_amount_conditions: dict[str, int] = {}
    if "Release Shard" in items_pool and goal_conditions["release_shards"]:
        goal_amount_conditions["Release Shard"] = items_pool.count("Release Shard")
        while "Release Shard" in items_pool:
            items_pool.remove("Release Shard")
    if "Auto-Release Shard" in items_pool and goal_conditions["auto_release_shards"]:
        goal_amount_conditions["Auto-Release Shard"] = items_pool.count("Auto-Release Shard")
        while "Auto-Release Shard" in items_pool:
            items_pool.remove("Auto-Release Shard")
    if "Collect Shard" in items_pool and goal_conditions["collect_shards"]:
        goal_amount_conditions["Collect Shard"] = items_pool.count("Collect Shard")
        while "Collect Shard" in items_pool:
            items_pool.remove("Collect Shard")
    if "Auto-Collect Shard" in items_pool and goal_conditions["auto_collect_shards"]:
        goal_amount_conditions["Auto-Collect Shard"] = items_pool.count("Auto-Collect Shard")
        while "Auto-Collect Shard" in items_pool:
            items_pool.remove("Auto-Collect Shard")
    if "Macguffin" in items_pool and goal_conditions["macguffin_collection"]:
        goal_amount_conditions["Macguffin"] = items_pool.count("Macguffin")
        while "Macguffin" in items_pool:
            items_pool.remove("Macguffin")

    if goal_conditions["giant_crystal"]:
        if "Giant Hint Crystal" in items_pool:
            goal_amount_conditions["Giant Hint Crystal"] = items_pool.count("Giant Hint Crystal")
            while "Giant Hint Crystal" in items_pool:
                items_pool.remove("Giant Hint Crystal")
        if "Big Hint Crystal" in items_pool:
            goal_amount_conditions["Big Hint Crystal"] = items_pool.count("Big Hint Crystal")
            while "Big Hint Crystal" in items_pool:
                items_pool.remove("Big Hint Crystal")
        if "Medium Hint Crystal" in items_pool:
            goal_amount_conditions["Medium Hint Crystal"] = items_pool.count("Medium Hint Crystal")
            while "Medium Hint Crystal" in items_pool:
                items_pool.remove("Medium Hint Crystal")
        if "Small Hint Crystal" in items_pool:
            goal_amount_conditions["Small Hint Crystal"] = items_pool.count("Small Hint Crystal")
            while "Small Hint Crystal" in items_pool:
                items_pool.remove("Small Hint Crystal")
        if "Mini Hint Crystal" in items_pool:
            goal_amount_conditions["Mini Hint Crystal"] = items_pool.count("Mini Hint Crystal")
            while "Mini Hint Crystal" in items_pool:
                items_pool.remove("Mini Hint Crystal")

    # if items_pool:
    #     goal_amount_conditions["Filler"] = len(items_pool)

    conds = set(
        (condition, amount) for condition, amount in goal_amount_conditions.items() if amount
    )

    r = And(*map(makeHas, conds))
    return r


def create_events(world: SLWorld) -> None:
    region = world.get_region("Admin Panel")
    region.add_event(
        "Goal",
        "Victory",
        rule=make_goal_from_item_pool(world),
        location_type=SLLocation,
        item_type=items.SLItem
    )
