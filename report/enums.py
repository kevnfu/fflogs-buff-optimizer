from enum import Enum, auto

class Encounter(Enum):
    OMEGA = 1068
    DSU = 1065
    TEA = 1062
    UCOB = 1060
    UWU = 1061
    P1 = 78
    P2 = 79
    P3 = 80
    P4I = 81
    P4II = 82
    P5 = 83
    P6 = 84
    P7 = 85
    P8 = 86

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
    JULY12 = 'rHq4kRnmKcbpgwZY'
    JULY16 = 'tbXZ3WJf9czhQyD6'
    JULY18 = 'TwzV7fmdhpA1gykF'
    JULY19 = '19M43vwFh6GtAcCp'
    JULY20 = 'Tm8K39AaBpYwD4MR'
    JULY23 = 'NvPKDTd3nfGF78Jp'
    JULY25 = 'Q6GnmtMY9y3NrBLz'
    JULY27MIRA = 'NJCPxY9vFVb3zZKG'
    JULY30 = 'tpLkJQNg96v2q4Pc'
    AUG2 = 'XhkGKxmc3HyAV16q'
    AUG4MIRA = 'P8BTFVXRvfMkr1gd'
    AUG8 = '4DWQwRnAgf3j2b1J'
    AUG9 = '87YtrHC16y3bXQGp'
    AUG15 = 'YaAhTkyzxRjq4wKW'
    AUG16 = '8kfYdVwLhTG9PXtc'
    AUG30 = 'w4jC8xtcGv7zLWY9'
    AUG31MIRA = '3ztRK87WNCFbPg6n'
    OMEGA_1 = 'Vh1GCwfkRALdbT4N'
    
class Vod(Enum):
    def __init__(self, offset: str, fight_id: int,  url: str=None) -> None:
        self.code = ReportCodes[self.name].value
        self.offset = offset
        self.fight_id = fight_id
        self.url = url

class Kevin(Vod):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.platform = Platform.YOUTUBE_LINK

    JULY16 = '3:14', 1, 'oflg8S4SkS4'
    JULY18 = '3:19', 1, 'Nay_Yc4lJR4'
    JULY19 = '0:47', 1, 'bZ8zohRxerk'
    JULY25 = '1:25', 1, '7YqJ-wkDwvc'
    JULY30 = '0:34', 1, 'GxnxeCD8sqw'
    AUG2 = '1:48', 1, '_dvbrYVDoVM'
    AUG15 = '0:53', 2, 'NBFbhur1CmI'
    AUG16 = '5:44', 1, 'l5JeYUCQlfc'

class Yoon(Vod):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.platform = Platform.TWITCH

    JULY16 = '3:57', 1, '1533793190'
    JULY18 = '3:01', 1, '1536014750'
    JULY19 = '1:48', 1, '1536993110'
    JULY20 = '2:56', 2, '1538012812'
    JULY23 = '13:25', 1, '1540569628'
    JULY25 = '02:56', 1, '1542924507'
    JULY30 = '0:53', 1, '1547494612'
    AUG15 = '0:26', 2, '1563342772'
    AUG16 = '3:33', 1, '1564194435'
    AUG30 = '3:19', 1, '1577479090'

class Anna(Vod):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.platform = Platform.TWITCH
    JULY19 = '6:36', 1, '1536992608'
    JULY20 = '19:18', 2, '1537996395'
    JULY23 = '26:43', 1, '1540556773'
    JULY25 = '03:32', 1, '1542923962'
    JULY30 = '3:30', 1, '1547492075'
    AUG2 = '2:06', 1, '1550755120'
    AUG8 = '2:57', 1, '1556535385'
    AUG9 = '3:27', 1, '1557483799'
    AUG15 = '8:11', 25, '1563342772'
    AUG16 = '9:43', 1, '1564187787'

class Aaron(Vod):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.platform = Platform.TWITCH
    JULY19 = '1:21', 13, '1537048452'
    JULY20 = '4:09', 2, '1538011686'
    JULY23 = '16:01', 1, '1540567419'
    JULY25 = '3:51', 1, '1542923664'
    JULY30 = '2:07', 1, '1547493441'
    AUG2 = '3:53', 1, '1550753649'
    AUG8 = '5:07', 1, '1556533630'
    AUG9 = '0:55', 1, '1557483799'
    AUG15 = '0:58', 2,'1563237971'
    AUG16 = '2:01', 1, '1564195958'

class Sarah(Vod):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.platform = Platform.TWITCH
    JULY25 = '1:28', 1, '1542925929'

class Blake(Vod):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.platform = Platform.TWITCH
    JULY12 = '11:36', 1, '1529282919'
    JULY16 = '10:49', 1, '1533786990'

class Mira(Vod):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.platform = Platform.TWITCH
    JULY27MIRA = '00:55', 24, '1543800290'
    AUG4MIRA = '6:31', 1, '1552616781'
    AUG31MIRA = '1:14', 1, '1578536320'
    OMEGA_1 = '2:07', 1, '1717620670'
