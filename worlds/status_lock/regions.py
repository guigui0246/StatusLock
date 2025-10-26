from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Region

if TYPE_CHECKING:
    from .world import SLWorld


def create_and_connect_regions(world: SLWorld) -> None:
    create_all_regions(world)
    connect_regions(world)


def create_all_regions(world: SLWorld) -> None:
    regions = [Region("Admin Panel", world.player, world.multiworld)]
    world.multiworld.regions += regions


def connect_regions(world: SLWorld) -> None:
    # Nothing here
    pass
