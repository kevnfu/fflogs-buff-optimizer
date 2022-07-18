from enum import Enum, auto

class Encounter(Enum):
    DSU = 1065

class Platform(Enum):
    YOUTUBE = auto()
    YOUTUBE_LINK = auto()
    TWITCH = auto()

# statics in FFlogs are guilds?
class Guild(Enum):
    DUMMY_DOWN = 80813
