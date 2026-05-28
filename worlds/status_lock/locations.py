from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Location, LocationProgressType

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


def create_events(world: SLWorld) -> None:
    region = world.get_region("Admin Panel")
    region.add_event("Goal", "Victory", location_type=SLLocation, item_type=items.SLItem)
