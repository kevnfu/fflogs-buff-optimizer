from enum import Enum, auto

class Encounter(Enum):
    DSU = 1065
    TEA = 1062
    UCOB = 1060
    UWU = 1061
    P1 = 78
    P2 = 79
    P3 = 80
    P4I = 81
    P4II = 82

class Platform(Enum):
    YOUTUBE = auto()
    YOUTUBE_LINK = auto()
    TWITCH = auto()

# statics in FFlogs are guilds?
class Guild(Enum):
    DUMMY_DOWN = 80813
    SINGLES_FOR_AARON = 94380

class User(Enum):
    KEVIN = 215343

class ReportCodes(Enum):
    JULY23 = "NvPKDTd3nfGF78Jp"
    JULY26 = "Q6GnmtMY9y3NrBLz"
    
class Yoon(Enum):
    JULY23 = 1540569628, '13:27', 1

    def __init__(self, code: int, offset: str, fight_id: int) -> None:
        self.code = code
        self.offset = offset
        self.fight_id = fight_id
