from mission_control import MissionGenerator
from gsheet_rw import MissionWriter, EthogramReader, gc
import datetime
import utils

url = "https://docs.google.com/spreadsheets/d/1P8Rl8HGEIn_lfnzyQlHL4U3znqM2UT24JiRgdh3A-kM/edit#gid=0"

class WritePipeline:
    def __init__(
        self,
        first_departure_duration,
        last_departure_duration,
        date=None,
        mission_duration=1200,
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
            min_duration_factor=noise_factor,
            date=self.date,
            mission_duration=mission_duration,
        )

        self.GS = MissionWriter(url)
        self.wks = self.GS.get_worksheet()

    def run(self):
        # Delete today's mission if any exist.
        self.delete_today()

        # Append today's mission.
        self.append_mission()

    def append_mission(self):
        mission = self.M.generate_mission()

        df = utils.get_as_dataframe(self.wks)
        start_index = df.index[df.iloc[:,:1].isnull().all(axis=1)][0]

        self.GS.populate_sheet(self.wks, mission, start_index)

    def delete_today(self):
        """
        Find any existing rows where date is today and delete.

        :param wks: Worksheet object
        :return:
        """
        # Read worksheet in as dataframe.
        df = utils.get_as_dataframe(self.wks)

        # Find rows for today's date.
        rows = df.index[df["date"] == self.date]

        if not rows.empty:
            start_index = int(rows[0])
            end_index = int(rows[-1])

            # Delete.
            self.wks.delete_rows(start_index, end_index)


class ReadPipeline:
    def __init__(self, url=url, worksheet_name="Data"):
        self.url = url
        self.worksheet_name = worksheet_name
        self.gc = gc
        self.sh = self.gc.open_by_url(self.url)
        self.wks = self.sh.worksheet(worksheet_name)

    def read(self, explode_ethogram=True):
        df = EthogramReader(self.url, self.worksheet_name).run(explode_ethogram)

        return df

if __name__ == "__main__":
    R = ReadPipeline()
    df = R.read(explode_ethogram=True)
    condensed = R.read(explode_ethogram=False)

    from plotting import plot_departures, EthogramVisualizer
    plot_departures(condensed, 15)

    E = EthogramVisualizer(df)
    E.plot_ethogram()
    E.plot_percent_behavior("Away")
    E.plot_percent_behavior("Lying")
