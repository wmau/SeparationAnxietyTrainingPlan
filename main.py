from mission_control import MissionGenerator
from gsheet_rw import MissionWriter
import datetime

url = "https://docs.google.com/spreadsheets/d/1P8Rl8HGEIn_lfnzyQlHL4U3znqM2UT24JiRgdh3A-kM/edit#gid=0"


class WritePipeline:
    def __init__(
        self,
        first_departure_duration,
        last_departure_duration,
        date=None,
        noise_factor=0.5,
        url=url,
    ):
        """
        Strings together the mission generator pipeline and the mission writer
        pipeline.

        """
        if date is None:
            date = str(datetime.datetime.now().date())
        if isinstance(date, datetime.datetime):
            date = str(date)
        self.date = date

        self.M = MissionGenerator(
            first_departure_duration,
            last_departure_duration,
            noise_factor=noise_factor,
            date=self.date,
        )

        self.GS = MissionWriter(url)

    def run(self):
        mission = self.M.generate_mission()

        # Get the worksheet and populate it.
        wk = self.GS.get_worksheet(self.date)
        self.GS.populate_sheet(wk, mission)


if __name__ == "__main__":
    P = WritePipeline(16, 80, noise_factor=0.5)
    P.run()
