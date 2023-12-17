from mission_control import Mission
from gsheet_rw import WriteMission
import datetime

class Pipeline:
    def __init__(self, date=None):
        if date is None:
            date = datetime.datetime.now().date()

        M = Mission()