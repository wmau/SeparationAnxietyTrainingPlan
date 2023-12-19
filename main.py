from mission_control import Mission
from gsheet_rw import WriteMission
import datetime

url = "https://docs.google.com/spreadsheets/d/1P8Rl8HGEIn_lfnzyQlHL4U3znqM2UT24JiRgdh3A-kM/edit#gid=0"


class WritePipeline:
    def __init__(
        self,
        first_departure_duration,
        last_departure_duration,
        date=None,
        noise_factor=0.8,
        url=url,
    ):
        if date is None:
            date = datetime.datetime.now().date()

        self.M = Mission(
            first_departure_duration,
            last_departure_duration,
            noise_factor=noise_factor,
            date=date,
        )
        self.mission = self.M.generate_mission()

        self.GS = WriteMission(url)

    def run(self):
        wk = self.GS.get_worksheet(str(self.mission["date"].unique()[0]))
        self.GS.populate_sheet(wk, self.mission)


if __name__ == "__main__":
    P = WritePipeline(10, 50)
    P.run()
