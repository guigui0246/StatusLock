CLIENT_PREFIX = "!admin "
WEBSITE_PREFIX = ""
CONNECT_ADMIN = "login {password}"
HINT_COST = "/option hint_cost {cost}"
RELEASE = "/option release_mode {mode}"
COLLECT = "/option collect_mode {mode}"
COUNTDOWN = "/countdown seconds={seconds}"  # To make a countdown before /release or /collect
RELEASE_PLAYER = "/release {player_name}"  # To auto-release if someone isn't connected
COLLECT_PLAYER = "/collect {player_name}"  # To auto-collect if someone isn't connected
# In case we add free hints:
HINT = "/hint {player_name} {item_name}"  # To request a hint for a specific item
HINT_LOCATION = "/hint_location {player_name} {location_name}"  # To request a hint for a specific location
