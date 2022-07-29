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
    JULY18 = "TwzV7fmdhpA1gykF"
    JULY19 = "19M43vwFh6GtAcCp"
    JULY20 = "Tm8K39AaBpYwD4MR"
    JULY23 = "NvPKDTd3nfGF78Jp"
    JULY26 = "Q6GnmtMY9y3NrBLz"
    JULY27MIRA = "NJCPxY9vFVb3zZKG"
    
class Vod(Enum):
    def __init__(self, code: ReportCodes, offset: str, fight_id: int,  url: str=None) -> None:
        self.code = code.value
        self.offset = offset
        self.fight_id = fight_id
        self.url = url

class Kevin(Vod):
    JULY18 = ReportCodes.JULY18, '3:19', 1, 'Nay_Yc4lJR4'
    JULY19 = ReportCodes.JULY19, '0:47', 1, 'bZ8zohRxerk'
    JULY26 = ReportCodes.JULY26, '1:25', 1, '7YqJ-wkDwvc'

class Yoon(Vod):
    JULY23 = ReportCodes.JULY23, '13:27', 1, '1540569628'
    JULY26 = ReportCodes.JULY26, '02:56', 1, '1542924507'

class Anna(Vod):
    JULY26 = ReportCodes.JULY26, '03:32', 1, '1542923962'

class Mira(Vod):
    JULY27 = ReportCodes.JULY27MIRA, '00:55', 24, '1543800290'