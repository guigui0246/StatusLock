from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld

from .options import option_groups, option_presets


# For our game to display correctly on the website, we need to define a WebWorld subclass.
class SLWebWorld(WebWorld):
    game = "SL"
    theme = "grass"

    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Status Lock for MultiWorld.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Guigui0246"],
    )
    setup_fr = Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Status Lock for MultiWorld.",
        "French",
        "setup_fr.md",
        "setup/fr",
        ["Guigui0246"],
    )

    # We add these tutorials to our WebWorld by overriding the "tutorials" field.
    tutorials = [setup_en, setup_fr]

    # If we have option groups and/or option presets, we need to specify these here as well.
    option_groups = option_groups
    options_presets = option_presets
