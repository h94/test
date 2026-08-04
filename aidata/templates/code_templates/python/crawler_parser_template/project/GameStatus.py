from enum import Enum
#無使用, 已轉移到AppSettings 這邊只是留著對照用
class GameStatus(Enum):
    InProgress = "0"
    Final = "1"
    Scheduled = "2"
    Postponed = "3"
    Cancelled = "4"
