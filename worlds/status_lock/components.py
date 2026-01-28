from worlds.LauncherComponents import Component, Type, components
from worlds.LauncherComponents import launch  # type: ignore[reportMissingTypeStubs]


def run_client(*args: str) -> None:
    from .client import main

    launch(main, name="Status Lock Client", args=args)


components.append(
    Component(
        "Status Lock Client",
        func=run_client,
        game_name="Status Lock",
        component_type=Type.CLIENT,
        supports_uri=True,
    )
)
print("Registered Status Lock Client component")
