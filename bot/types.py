import dataclasses
import datetime

@dataclasses.dataclass
class Status:
    ip: str
    time: datetime.datetime
