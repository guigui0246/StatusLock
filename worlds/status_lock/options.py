from dataclasses import dataclass
from enum import Flag
from typing import Any

from Options import Choice, OptionGroup, PerGameCommonOptions, Range, Toggle


class MultipleGoals(Toggle):
    """
    Enables multiple goals needing to be reached to goal.
    This has no effect yet.
    TODO: implement multiple goals logic.
    """

    display_name = "Multiple Goals"
    default = False


class GoalType(Flag):
    """
    The type of goal to reach.
    """
    release_shards = 1 << 0
    auto_release_shards = 1 << 1
    collect_shards = 1 << 2
    auto_collect_shards = 1 << 3
    giant_crystal = 1 << 4
    filler_completion = 1 << 5
    macguffin_collection = 1 << 6


class GoalChoice(Choice):
    """
    The goal(s) to reach to win the game.
    """

    display_name = "Goal(s) Choice"

    option_all_release_shards = GoalType.release_shards
    option_all_auto_release_shards = GoalType.auto_release_shards
    option_all_collect_shards = GoalType.collect_shards
    option_all_auto_collect_shards = GoalType.auto_collect_shards
    option_all_shards = (
        GoalType.release_shards |
        GoalType.auto_release_shards |
        GoalType.collect_shards |
        GoalType.auto_collect_shards
    )
    option_giant_crystal = GoalType.giant_crystal
    alias_all_crystal = option_giant_crystal
    option_everyprogression = option_all_shards | GoalType.giant_crystal
    alias_evertprog = option_everyprogression

    option_filler_completion = GoalType.filler_completion
    option_macguffin_collection = GoalType.macguffin_collection
    option_everything = (
        option_everyprogression |
        GoalType.filler_completion |
        GoalType.macguffin_collection
    )

    default = option_giant_crystal


class MultipleGoalsAmount(Range):
    """
    How many goals need to be reached to win.
    Only has an effect if Multiple Goals is enabled.
    This has no effect yet.
    TODO: implement multiple goals logic.
    """

    display_name = "Multiple Goals Amount"
    range_start = 2
    range_end = 7
    default = 2


class ReleaseShardsAmount(Range):
    """
    How much release shards to place in the pool.
    Those are required to unlock release.
    If set to 0, release will be unlocked by default.
    """

    display_name = "Release Shards Amount"

    range_start = 0
    range_end = 100
    default = 5


class ReleaseShardsPercent(Range):
    """
    How much release shards you need to collect to unlock release.
    """

    display_name = "Release Shards Percent"

    range_start = 10
    range_end = 100
    default = 100


class AutoReleaseShardsAmount(Range):
    """
    How much auto-release shards to place in the pool.
    Those will only have an effect if the number of required release shards is reached.
    If set to 0, auto-release will be unlocked as soon as the required release shards are available.
    """

    display_name = "Auto-Release Shards Amount"

    range_start = 0
    range_end = 10
    default = 1


class AutoReleaseShardsPercent(Range):
    """
    How much auto-release shards you need to collect to unlock auto-release.
    """

    display_name = "Auto-Release Shards Percent"

    range_start = 10
    range_end = 100
    default = 100


class CollectShardsAmount(Range):
    """
    How much collect shards to place in the pool.
    Those are required to unlock collect.
    If set to 0, collect will be unlocked by default.
    """

    display_name = "Collect Shards Amount"

    range_start = 0
    range_end = 100
    default = 5


class CollectShardsPercent(Range):
    """
    How much collect shards you need to collect to unlock collect.
    """

    display_name = "Collect Shards Percent"

    range_start = 10
    range_end = 100
    default = 100


class AutoCollectShardsAmount(Range):
    """
    How much auto-collect shards to place in the pool.
    Those will only have an effect if the number of required collect shards is reached.
    If set to 0, auto-collect will be unlocked as soon as the required collect shards are available.
    """

    display_name = "Auto-Collect Shards Amount"

    range_start = 0
    range_end = 10
    default = 1


class AutoCollectShardsPercent(Range):
    """
    How much auto-collect shards you need to collect to unlock auto-collect.
    """

    display_name = "Auto-Collect Shards Percent"

    range_start = 10
    range_end = 100
    default = 100


class MinHintCost(Range):
    """
    The minimum hint cost you can reduce to with crystals.
    If this is the same as the maximum hint cost, hints crystals will be removed from the item pool.
    """

    display_name = "Minimum Hint Cost"

    range_start = 1
    range_end = 100
    default = 2


class MaxHintCost(Range):
    """
    The maximum hint cost. This will be the starting hint cost before any crystals.
    If this is the same as the minimum hint cost, hints crystals will be removed from the item pool.
    """

    display_name = "Maximum Hint Cost"

    range_start = 1
    range_end = 100
    default = 100


class CrystalAmount(Range):
    """
    The amount of crystals present in the game.
    If this is 0, hint crystals will be removed from the item pool and hint cost will be random between min and max.
    If this is too much compared to the hint cost range, some crystals will be mini crystals.
    Mini crystals give 0% but can be merged into small crystals at a calculated rate depending on the hint cost range.
    Other crystals (small, medium, big, giant) give respectively 1%, 5%, 20% and 80% of the hint cost range.
    """

    display_name = "Crystal Amount"

    range_start = 0
    range_end = 1000
    default = 35


class MacGuffinAmount(Range):
    """
    The amount of MacGuffins to collect to goal if the macguffin goal is active.
    This still adds macguffins to the item pool even if the goal is not active.
    TODO: change that behavior to only add them if the goal is active.
    """

    display_name = "MacGuffin Amount"

    range_start = 1
    range_end = 1000
    default = 50


class TrapChance(Range):
    """
    The chance for a filler item to be a trap instead of a harmless filler.
    Traps have no effect yet.
    TODO: implement trap effects.
    """

    display_name = "Trap Chance (%)"

    range_start = 0
    range_end = 90
    default = 10


# We must now define a dataclass inheriting from PerGameCommonOptions that we put all our options in.
# This is in the format "option_name_in_snake_case: OptionClassName".
@dataclass
class SLOptions(PerGameCommonOptions):
    multi_goals: MultipleGoals
    goal_choice: GoalChoice
    multiple_goals_amount: MultipleGoalsAmount
    release_shards_amount: ReleaseShardsAmount
    release_shards_percent: ReleaseShardsPercent
    auto_release_shards_amount: AutoReleaseShardsAmount
    auto_release_shards_percent: AutoReleaseShardsPercent
    collect_shards_amount: CollectShardsAmount
    collect_shards_percent: CollectShardsPercent
    auto_collect_shards_amount: AutoCollectShardsAmount
    auto_collect_shards_percent: AutoCollectShardsPercent
    min_hint_cost: MinHintCost
    max_hint_cost: MaxHintCost
    crystal_amount: CrystalAmount
    macguffin_amount: MacGuffinAmount
    trap_chance: TrapChance


ALL_OPTIONS = [
    "multi_goals",
    "goal_choice",
    "multiple_goals_amount",
    "release_shards_amount",
    "release_shards_percent",
    "auto_release_shards_amount",
    "auto_release_shards_percent",
    "collect_shards_amount",
    "collect_shards_percent",
    "auto_collect_shards_amount",
    "auto_collect_shards_percent",
    "min_hint_cost",
    "max_hint_cost",
    "crystal_amount",
    "macguffin_amount",
]


option_groups = [
    OptionGroup(
        "Goal Settings",
        [MultipleGoals, GoalChoice, MultipleGoalsAmount],
    ),
    OptionGroup(
        "Release Settings",
        [ReleaseShardsAmount, ReleaseShardsPercent, AutoReleaseShardsAmount, AutoReleaseShardsPercent],
    ),
    OptionGroup(
        "Collect Settings",
        [CollectShardsAmount, CollectShardsPercent, AutoCollectShardsAmount, AutoCollectShardsPercent],
    ),
    OptionGroup(
        "Crystal Settings",
        [MinHintCost, MaxHintCost, CrystalAmount],
    ),
    OptionGroup(
        "MacGuffin Settings",
        [MacGuffinAmount],
    ),
]


# Finally, we can define some option presets if we want the player to be able to quickly choose a specific "mode".
option_presets: dict[str, dict[str, Any]] = {
    "elire's original": {
        "multi_goals": False,
        "goal_choice": GoalChoice.option_everyprogression,
        "release_shards_amount": 5,
        "release_shards_percent": 100,
        "auto_release_shards_amount": 0,
        "auto_release_shards_percent": 100,
        "collect_shards_amount": 5,
        "collect_shards_percent": 100,
        "auto_collect_shards_amount": 0,
        "auto_collect_shards_percent": 100,
        "min_hint_cost": 1,
        "max_hint_cost": 100,
        "crystal_amount": 50,
        "macguffin_amount": 0,
        "trap_chance": 0,
    },
    "extreme mode": {
        "multi_goals": False,
        "goal_choice": GoalChoice.option_everything,
        "release_shards_amount": 100,
        "release_shards_percent": 100,
        "auto_release_shards_amount": 10,
        "auto_release_shards_percent": 100,
        "collect_shards_amount": 100,
        "collect_shards_percent": 100,
        "auto_collect_shards_amount": 10,
        "auto_collect_shards_percent": 100,
        "min_hint_cost": 1,
        "max_hint_cost": 100,
        "crystal_amount": 1000,
        "macguffin_amount": 1000,
        "trap_chance": 90,
    },
}
