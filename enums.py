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
    JULY12 = "rHq4kRnmKcbpgwZY"
    JULY16 = "tbXZ3WJf9czhQyD6"
    JULY18 = "TwzV7fmdhpA1gykF"
    JULY19 = "19M43vwFh6GtAcCp"
    JULY20 = "Tm8K39AaBpYwD4MR"
    JULY23 = "NvPKDTd3nfGF78Jp"
    JULY25 = "Q6GnmtMY9y3NrBLz"
    JULY27MIRA = "NJCPxY9vFVb3zZKG"
    JULY30 = "tpLkJQNg96v2q4Pc"
    AUG02 = "XhkGKxmc3HyAV16q"
    
class Vod(Enum):
    def __init__(self, code: ReportCodes, offset: str, fight_id: int,  url: str=None) -> None:
        self.code = code.value
        self.offset = offset
        self.fight_id = fight_id
        self.url = url

class Kevin(Vod):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.platform = Platform.YOUTUBE_LINK

    JULY16 = ReportCodes.JULY16, '3:14', 1, 'oflg8S4SkS4'
    JULY18 = ReportCodes.JULY18, '3:19', 1, 'Nay_Yc4lJR4'
    JULY19 = ReportCodes.JULY19, '0:47', 1, 'bZ8zohRxerk'
    JULY25 = ReportCodes.JULY25, '1:25', 1, '7YqJ-wkDwvc'
    JULY30 = ReportCodes.JULY30, '0:34', 1, 'GxnxeCD8sqw'
    AUG02 = ReportCodes.AUG02, '1:48', 1, '_dvbrYVDoVM'

class Yoon(Vod):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.platform = Platform.TWITCH

    JULY16 = ReportCodes.JULY16, '3:57', 1, '1533793190'
    JULY18 = ReportCodes.JULY18, '3:01', 1, '1536014750'
    JULY19 = ReportCodes.JULY19, '1:48', 1, '1536993110'
    JULY20 = ReportCodes.JULY20, '2:56', 2, '1538012812'
    JULY23 = ReportCodes.JULY23, '13:25', 1, '1540569628'
    JULY25 = ReportCodes.JULY25, '02:56', 1, '1542924507'
    JULY30 = ReportCodes.JULY30, '0:53', 1, '1547494612'

class Anna(Vod):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.platform = Platform.TWITCH
    JULY19 = ReportCodes.JULY19, '6:36', 1, '1536992608'
    JULY20 = ReportCodes.JULY20, '19:18', 2, '1537996395'
    JULY23 = ReportCodes.JULY23, '26:43', 1, '1540556773'
    JULY25 = ReportCodes.JULY25, '03:32', 1, '1542923962'
    JULY30 = ReportCodes.JULY30, '3:30', 1, '1547492075'
    AUG02 = ReportCodes.AUG02, '2:06', 1, '1550755120'

class Aaron(Vod):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.platform = Platform.TWITCH
    JULY19 = ReportCodes.JULY19, '1:21', 13, '1537048452'
    JULY20 = ReportCodes.JULY20, '4:09', 2, '1538011686'
    JULY23 = ReportCodes.JULY23, '16:01', 1, '1540567419'
    JULY25 = ReportCodes.JULY25, '3:51', 1, '1542923664'
    JULY30 = ReportCodes.JULY30, '2:07', 1, '1547493441'
    AUG02 = ReportCodes.AUG02, '3:53', 1, '1550753649'

class Sarah(Vod):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.platform = Platform.TWITCH
    JULY25 = ReportCodes.JULY25, '1:28', 1, '1542925929'

class Blake(Vod):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.platform = Platform.TWITCH
    JULY12 = ReportCodes.JULY12, '11:36', 1, '1529282919'
    JULY16 = ReportCodes.JULY16, '10:49', 1, '1533786990'

class Mira(Vod):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.platform = Platform.TWITCH
    JULY27 = ReportCodes.JULY27MIRA, '00:55', 24, '1543800290'